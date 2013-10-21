/* Javascript for GeoWeb Map*/
var map;
var mercator = new OpenLayers.Projection("EPSG:900913");
var geographic = new OpenLayers.Projection("EPSG:4326");

var world = new OpenLayers.Bounds(-180, -89, 180, 89).transform(
    geographic, mercator
);
var center = new OpenLayers.LonLat(-121.90515908415186, 37.424431833728114).transform(
    geographic, mercator
);

function init() {
map = new OpenLayers.Map('map',{
	projection: new OpenLayers.Projection("EPSG:900913"),
      displayProjection: new OpenLayers.Projection("EPSG:4326"),
      units: "m",
      numZoomLevels: 16,
      maxResolution: 156543.0339,
      maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
						     20037508, 20037508.34),
	//maxExtent: world,
	//numZoomLevels: 10,
	controls: [
		new OpenLayers.Control.Navigation({}),
		new OpenLayers.Control.LayerSwitcher({}),
		//new OpenLayers.Control.ScaleLine(),
		new OpenLayers.Control.PanZoomBar(),
		new OpenLayers.Control.MousePosition(),
		],
	});

    var tonerlite = new OpenLayers.Layer.XYZ(
        "Toner-Lite",
        ["http://a.tile.stamen.com/toner-lite/${z}/${x}/${y}.png",
        "http://b.tile.stamen.com/toner-lite/${z}/${x}/${y}.png",
        "http://c.tile.stamen.com/toner-lite/${z}/${x}/${y}.png",
        "http://d.tile.stamen.com/toner-lite/${z}/${x}/${y}.png"],
        {wrapDateLine: true, visibility:true,
        buffer: 1,numZoomLevels: 16, minZoom:0,
        isBaseLayer:true,sphericalMecator:true}
        );

    var toner = new OpenLayers.Layer.XYZ(
        "Toner",
        ["http://a.tile.stamen.com/toner/${z}/${x}/${y}.png",
        "http://b.tile.stamen.com/toner/${z}/${x}/${y}.png",
        "http://c.tile.stamen.com/toner/${z}/${x}/${y}.png",
        "http://d.tile.stamen.com/toner/${z}/${x}/${y}.png"],
        {wrapDateLine: true, visibility:false,
        buffer: 1,numZoomLevels: 16, minZoom:0,
        isBaseLayer:true,sphericalMecator:true}
        );

    var terrain = new OpenLayers.Layer.XYZ(
        "Terrain",
        ["http://a.tile.stamen.com/terrain/${z}/${x}/${y}.png",
        "http://b.tile.stamen.com/terrain/${z}/${x}/${y}.png"],
        {wrapDateLine: true, visibility:false,
        buffer: 1,numZoomLevels: 18, minZoom:4,
        isBaseLayer:true,sphericalMecator:true}
        );

    var ceqapoints = new OpenLayers.Layer.XYZ(
        "CEQA Documents",
        ["http://ceqa.ice.ucdavis.edu/tiles/docpoints/${z}/${x}/${y}.png"],
        {wrapDateLine: true, enabled:false,
        buffer: 1,numZoomLevels: 16, minZoom:0,
        isBaseLayer:false,sphericalMecator:true}
        );

    var utfgrid = new OpenLayers.Layer.UTFGrid({
        url: "http://ceqa.ice.ucdavis.edu/tiles/docgrid/${z}/${x}/${y}.json",
        utfgridResolution: 4, // default is 2
        displayInLayerSwitcher: false
    });

    var matrixIds = new Array(26);
    for (var i=0; i<26; ++i) {
        matrixIds[i] = "EPSG:900913:" + i;
    }



    var callback = function(infoLookup) {
        var msg = "";
        if (infoLookup) {
            var info;
            for (var idx in infoLookup) {
            // idx can be used to retrieve layer from map.layers[idx]
                info = infoLookup[idx];
                if (info && info.data) {
                    msg += '<a href="/docdesp_noc/'+info.data.doc_pk+'">'+info.data.doc_pk+'</a>';
                    document.getElementById("attributes").innerHTML = msg;
                }
            }
        }
    
    };    
    
    var controls = {
    //move: new OpenLayers.Control.UTFGrid({
    //    callback: callback,
    //    handlerMode: "move"
    //    }),
    //hover: new OpenLayers.Control.UTFGrid({
    //    callback: callback,
    //    handlerMode: "hover"
    //    }),
    click: new OpenLayers.Control.UTFGrid({
        callback: callback,
        handlerMode: "click"
        })
    };
    
    for (var key in controls) {
        map.addControl(controls[key]);
    }   

    // activate the control that responds to mousemove
    //toggleControl({value: "click"});


    //Example wmts for later
    var wmtsbasins = new OpenLayers.Layer.WMTS(
    {name: "WMTS Basins",
    url: "http://geoweb.ice.ucdavis.edu/geoserver/gwc/service/wmts/",
    layer:"geoweb:groundwaterbasins4326",
    matrixSet: "EPSG:900913",
    matrixIds: matrixIds,
    format: "image/png",
    style: "_null",
    opacity: 0.5,
    isBaseLayer: false,
    visibility: false
    });


map.addLayers([tonerlite,toner,terrain,ceqapoints,utfgrid]);
map.setCenter(center);
map.zoomTo(6);
}
