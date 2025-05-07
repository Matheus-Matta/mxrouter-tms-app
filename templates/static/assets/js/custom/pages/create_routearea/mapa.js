
$(document).ready(function () {
    $('#bairro_select').select2({
        tags: true,
        tokenSeparators: [',', ' ']
    });
});

let map, drawnItems, routeGeoJSON = null;
const undoStack = [];
const MAX_UNDO = 20;
let outras_geojsons
const corRota = document.querySelector("#corRotaEdit").getAttribute("data-color");
document.addEventListener("DOMContentLoaded", () => {

    map = L.map("map").setView([-22.8, -42.9], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    map.pm.addControls({
        position: 'topright',
        drawPolygon: true,
        drawPolyline: false,
        drawMarker: false,
        drawCircleMarker: false,
        circleMarker: false,
        drawCircle: false,
        editMode: true,
        dragMode: false,
        removalMode: true,
        cutPolygon: true,
        snappable: false,
        snapMiddle: false
    });

    // Eventos do Leaflet.PM
    map.on('pm:create', (e) => {
        mostrarBotaoSalvar();
        registrarEventosPm(e.layer);
        
    });

    map.on('pm:cut', (e) => {
        mostrarBotaoSalvar();
        const original = e.originalLayer || e.layer;
        const result = e.resultLayer || e.result;

        if (original && map.hasLayer(original)) {
            map.removeLayer(original);
        }

        if (result?.eachLayer) {
            result.eachLayer((layer) => {
                map.addLayer(layer);
                registrarEventosPm(layer);
            });
        }
    });

    map.on('pm:remove', () => {
        mostrarBotaoSalvar();
    });

    map.on('pm:edit', () => {
        mostrarBotaoSalvar();
    });

    map.on('pm:dragend', () => {
        mostrarBotaoSalvar();
    });

    // Carrega o geojson inicial salvo no input, se houver
    const geojsonInput = document.getElementById("geojsonInput");
    outras_geojsons = JSON.parse(geojsonInput.getAttribute("data-other-routes"));
    adicionarOutrasRotas()
    if (geojsonInput && geojsonInput.value && geojsonInput.value !== "None") {
        try {
            const parsed = JSON.parse(geojsonInput.value);
            // Verifica se é um GeoJSON válido com 'type'
            if (parsed.type && (parsed.type === "Feature" || parsed.type === "FeatureCollection")) {
                routeGeoJSON = parsed;
                console.log(routeGeoJSON, outras_geojsons)
                L.geoJSON(routeGeoJSON, {
                    style: { color: corRota, weight: 2, fillOpacity: 0.50 }
                }).eachLayer(layer => {
                    map.addLayer(layer);
                    registrarEventosPm(layer);
                });
                const bounds = L.geoJSON(routeGeoJSON).getBounds();
                if (bounds.isValid()) {
                    map.fitBounds(bounds, { maxZoom: map.getZoom() });
                }
                atualizarDadosGeoJSON(routeGeoJSON);
            } else {
                console.error("❌ GeoJSON inválido: estrutura ausente ou incorreta.");
            }

        } catch (err) {
            console.error("Erro ao carregar GeoJSON inicial:", err);
        }
    }

});

function registrarEventosPm(layer) {
    if (!layer || !layer.on) return;
    layer.on('pm:edit', mostrarBotaoSalvar);
    layer.on('pm:remove', mostrarBotaoSalvar);
}

function mostrarBotaoSalvar() {
    document.getElementById("saveMap").classList.remove("hidden");
}

async function buscarBairro(query) {
    const dropdown = document.getElementById("dropdown");
    const loader = document.getElementById("loader");
    dropdown.innerHTML = "";
    loader.classList.remove("hidden"); // 👈 mostra o loader

    if (query.length < 2) {
        loader.classList.add("hidden");
        dropdown.classList.add("hidden");
        return;
    }

    try {
        const res = await fetch(`https://nominatim.openstreetmap.org/search?format=geojson&polygon_geojson=1&q=${encodeURIComponent(query)}&limit=5`);
        const data = await res.json();

        const features = data.features.filter(
            f => f.geometry && ["Polygon", "MultiPolygon"].includes(f.geometry.type)
        );

        if (!features.length) {
            dropdown.innerHTML = '<div class="px-4  py-2 text-gray-500">Nenhum bairro com polígono encontrado</div>';
        } else {
            features.forEach((item) => {
                const option = document.createElement("div");
                option.className = "px-4 py-2 border-b-2 border-gray-400 bg-gray-100 hover:bg-gray-200 cursor-pointer";
                option.textContent = item.properties.display_name;
                option.onclick = () => mostrarBairroSelecionado(item);
                dropdown.appendChild(option);
            });
        }

        dropdown.classList.remove("hidden");
    } catch (err) {
        console.error("Erro:", err);
        dropdown.innerHTML = '<div class="px-4 py-2 text-red-500">Erro ao buscar</div>';
        dropdown.classList.remove("hidden");
    } finally {
        loader.classList.add("hidden"); // 👈 esconde o loader no final
    }
}

function mostrarBairroSelecionado(feature) {
    if (!feature.geometry?.type.includes("Polygon")) return;

    const layer = L.geoJSON(feature, {
        style: { color: "red", weight: 2, fillOpacity: 0.3 }
    });

    layer.eachLayer((subLayer) => {
        map.addLayer(subLayer);
        registrarEventosPm(subLayer);
    });

    map.fitBounds(layer.getBounds());
    mostrarBotaoSalvar();
}

function salvarGeoJSON() {
    salvarEstadoAnterior();

    document.getElementById("saveMap").classList.add("hidden");

    const layers = Object.values(map._layers).filter(l =>
        l instanceof L.Polygon && typeof l.toGeoJSON === "function"
    );

    if (!layers.length) {
        routeGeoJSON = null;
        document.getElementById("geojsonInput").value = "";
        atualizarDadosGeoJSON(null);
        return;
    }

    let novoGeo = layers[0].toGeoJSON();
    for (let i = 1; i < layers.length; i++) {
        try {
            novoGeo = turf.union(novoGeo, layers[i].toGeoJSON());
        } catch (e) {
            console.error("Erro ao unir polígonos:", e);
            return;
        }
    }
    routeGeoJSON = novoGeo;

    if (outras_geojsons) {
        try {
            outras_geojsons.forEach((geo) => {
                try {
                    const outro = geo.geojson?.type === "Feature" ? geo.geojson : { type: "Feature", geometry: geo.geojson };
                    routeGeoJSON = turf.difference(routeGeoJSON, outro);
                } catch (e) {
                    console.warn("Erro ao subtrair rota:", e);
                }
            });
        } catch (e) {
            console.error("Erro ao interpretar outras rotas para subtração:", e);
        }
    }

    layers.forEach(l => map.removeLayer(l));

    L.geoJSON(routeGeoJSON, {
        style: { color: corRota, weight: 2, fillOpacity: 0.15 }
    }).eachLayer((layer) => {
        map.addLayer(layer);
        registrarEventosPm(layer);
    });
    
    adicionarOutrasRotas()
    salveGeojsonInput(routeGeoJSON)
    atualizarDadosGeoJSON(routeGeoJSON)
}

// Eventos do campo de busca
document.getElementById("bairroForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const termo = document.getElementById("bairroInput").value.trim();
    if (termo.length > 1) buscarBairro(termo);
});

document.addEventListener("click", (e) => {
    if (!e.target.closest("[data-kt-dropdown=true]")) {
        document.getElementById("dropdown").classList.add("hidden");
    }
});

function atualizarDadosGeoJSON(geojson) {
    if (!geojson || typeof geojson !== 'object') return;

    try {
        const area = turf.area(geojson); // em m²
        const distancia = turf.length(geojson, { units: 'kilometers' }); // em km (perímetro)

        const areaEl = document.getElementById("areaTotal");
        const distanciaEl = document.getElementById("distanciaTotal");
        const areaEl_ip = document.getElementById("areaTotalInput");
        const distanciaEl_ip = document.getElementById("distanciaTotalInput");

        areaEl_ip.value = area.toFixed(2);
        distanciaEl_ip.value = distancia.toFixed(2);

        if (areaEl) areaEl.textContent = `${area.toFixed(2)} m²`;
        if (distanciaEl) distanciaEl.textContent = `${distancia.toFixed(2)} km`;

    } catch (err) {
        console.error("Erro ao calcular área ou distância com Turf.js:", err);
    }
}

function salvarEstadoAnterior() {
    if (routeGeoJSON) {
        const clone = JSON.parse(JSON.stringify(routeGeoJSON));
        undoStack.push(clone);
    }
}

document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "z") {
        desfazerUltimaAlteracao();
    }
});

function desfazerUltimaAlteracao() {
    if (undoStack.length === 0) {
        return;
    }

    const ultimoEstado = undoStack.pop();
    routeGeoJSON = ultimoEstado;

    Object.values(map._layers).forEach(l => {
        if (l instanceof L.Polygon && typeof l.toGeoJSON === "function") {
            map.removeLayer(l);
        }
    });

    L.geoJSON(routeGeoJSON, {
        style: { color: corRota, weight: 2, fillOpacity: 0.15 }
    }).eachLayer((layer) => {
        map.addLayer(layer);
        registrarEventosPm(layer);
    });

    if (undoStack.length > 1) {
        mostrarBotaoSalvar();
    }

    if (undoStack.length > 1) () => mostrarBotaoSalvar();
    
    salveGeojsonInput(routeGeoJSON)
}
function salveGeojsonInput(geojson) {
    const geoinput = document.getElementById("geojsonInput");
    if (geojson) {
        geoinput.value = JSON.stringify(geojson);
    }
}

function recalcularGeoJSON() {
    const layers = [];

    map.eachLayer(layer => {
        if (layer instanceof L.Polygon && typeof layer.toGeoJSON === "function") {
            layers.push(layer);
        }
    });

    if (!layers.length) {
        routeGeoJSON = null;
        return;
    }

    let novoGeo = layers[0].toGeoJSON();
    for (let i = 1; i < layers.length; i++) {
        try {
            novoGeo = turf.union(novoGeo, layers[i].toGeoJSON());
        } catch (e) {
            console.error("Erro ao unir após remoção:", e);
        }
    }

    routeGeoJSON = novoGeo;
    atualizarDadosGeoJSON(routeGeoJSON);
    salveGeojsonInput(routeGeoJSON);
}

function adicionarOutrasRotas(){
    if (outras_geojsons) {
        try {
            outras_geojsons.forEach((geojson) => {
                console.log(geojson)
                if (geojson && geojson.geojson && geojson.geojson.type) {
                    L.geoJSON(geojson.geojson, {
                        style: {
                            color: "gray",
                            weight: 1,
                            fillOpacity: 0.50
                        }
                    }).addTo(map);
                }
            });
        } catch (err) {
            console.error("Erro ao carregar outras rotas GeoJSON:", err);
        }
    }
}