import flask
from elasticsearch import Elasticsearch
from flask import Flask, request, send_from_directory, render_template_string, render_template, jsonify, Response, redirect, url_for
import requests
import json, os
import Geohash, json, os
import collections,operator
from collections import defaultdict
import math, decimal
from geopy.distance import great_circle
import numpy as np
application = Flask(__name__)

"""import flask
from elasticsearch import Elasticsearch
from flask import Flask, request, send_from_directory, render_template_string, render_template, jsonify, Response, redirect, url_for
import requests
import json, os
import Geohash, json, os
import collections,operator
from collections import defaultdict
import math, decimal
from geopy.distance import great_circle
import numpy as np
application = Flask(__name__)

"""
Location
Rescue
Flood mapping
Directions
Disaster mapping
Routing
Matching
Disaster Response
Social Media
"""


def make_map(centroid,shelter_data,rescue_data,photon_shelter,photon_rescue,other_sh,other_res):

    with open("_Data/OSM_features_icons_dict.json") as f:
        OSM_features_icons_dict = json.dumps(json.load(f))

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8' />
        <title></title>
        <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
        <script src='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.js'></script>
        <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css' rel='stylesheet' />
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/bootstrap/3/css/bootstrap.css" />
        <style>
            body, html{
                height: 100%;
                width : 100%;
                padding: 0;
            }
            body{
                background-color: #CAD2D3;
            }
            .container {
                width: 100%;
                //padding: 10px;
                height: 100%
            }
            .one {
                float: left;
                height: 100%;
                width : 24%;
                padding-top: 10px;
                margin-left: -4px;
            }
            .two {
                margin-left: 10%;
                height: 100%;
                width: 80%;
            }
            #map {  position:absolute;
                    top:0; bottom:0; width:75%; transition: all 0.3s; margin-left: 14%;}
            .button { color: #fff; background-color: #555; padding: 1em; margin: 1em; position: absolute; right: 1em; top: 1em; border-radius: 0.5em; border-bottom: 2px #222 solid; cursor: pointer; }
            #resizeMap { top: 5em; }
            #instructions {
                position: absolute;
                margin-left: 30%;
                margin-top: 30%;
                height: 30%;
                width: 20%;
                top: 0;
                bottom: 0;
                padding: 10px;
                background-color: rgba(202,210,211, 0.7);
                overflow-y: scroll;
                display: none;
                color: rgb(0,63,121);
            }
            .map-overlay {
                font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
                position: absolute;
                width: 25%;
                top: 0;
                left: 0;
                padding: 10px;
            }
            .popup {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }
            .popup .popuptext {
                visibility: hidden;
                width: 160px;
                background-color: #555;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px 0;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -80px;
            }
            .popup .popuptext::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #555 transparent transparent transparent;
            }
            .popup .show {
                visibility: visible;
                -webkit-animation: fadeIn 1s;
                animation: fadeIn 1s
            }
            /* Add animation (fade in the popup) */
            @-webkit-keyframes fadeIn {
                from {opacity: 0;}
                to {opacity: 1;}
            }
            @keyframes fadeIn {
                from {opacity: 0;}
                to {opacity:1 ;}
            }
            input[type=text] {
                background-color: transparent;
                color: black;
                //border: 2px solid white;
                border-radius: 4px;
                width: 100%;
            }
            input[type=text]:focus {
                background-color: lightblue;
                color: black;
                border: 2px solid white;
                border-radius: 4px;
            }
            .mapboxgl-popup {
                max-width: 400px;
                font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            }
            #thumbnailwrapper {
                color:#2A2A2A;margin-right:5px;
                border-radius:0.2em;
                margin-bottom:5px;
                background-color:white;
                padding:5px;
                //border-color:#DADADA;
                border-style:solid;
                border-width:thin;
                font-size:15px
                text-align: center;
            }
            #thumbnailwrapper:hover{box-shadow:0 0 5px 5px #DDDDDD}
            #artiststhumbnail {
                width:100%;
                height:25%;
                overflow:hidden;
                //border-color:#DADADA;
                //border-style:solid;
                border-width:thin;
                //background-color:gray;
            }
            #artiststhumbnail:hover {left:50px }
            #genre {
                font-size:12px;
                font-weight:bold;
                color:#2A2A2A
            }
            #artiststhumbnail a img {
                display : block;
                margin : auto;
            }
            #loading {
                //position: absolute;
                width: 75%; height: 100%; background: url('/static/Preloader_3.gif') no-repeat center center;
            }
            #loader {
                float: left;
                position:absolute;
                height:100%;
                width:100%;
                background:gray;
                -ms-opacity:0.5;
                opacity:0.5;
                //z-index:1000000;
                display: none;
                //margin-left: -40px;
                //margin-top: -19px;
            }
            #menu {
                background: #fff;
                position: absolute;
                z-index: 1;
                top: 10px;
                right: 10px;
                border-radius: 3px;
                width: 120px;
                border: 1px solid rgba(0,0,0,0.4);
                font-family: 'Open Sans', sans-serif;
            }
            #menu a {
                font-size: 13px;
                color: #404040;
                display: block;
                margin: 0;
                padding: 0;
                padding: 10px;
                text-decoration: none;
                border-bottom: 1px solid rgba(0,0,0,0.25);
                text-align: center;
            }
            #menu a:last-child {
                border: none;
            }
            #menu a:hover {
                background-color: #f8f8f8;
                color: #404040;
            }
            #menu a.active {
                background-color: #3887be;
                color: #ffffff;
            }
            #menu a.active:hover {
                background: #3074a4;
            }
            .radio input[type='radio'] {
              display: none;
              /*removes original button*/
            }

            .radio label:before {
              /*styles outer circle*/
              content: " ";
              display: inline-block;
              position: relative;
              top: 5px;
              margin: 0 5px 0 0;
              width: 20px;
              height: 20px;
              border-radius: 11px;
              border: 2px solid orange;
              background-color: transparent;
            }

            .radio label {
              position: relative;
            }

            .radio label input[type='radio']:checked+span {
              /*styles inside circle*/
              border-radius: 11px;
              width: 12px;
              height: 12px;
              position: absolute;
              top: 9px;
              left: 24px;
              display: block;
              background-color: blue;
            }
            

            .btn {
                background-color: white; 
                color: black; 
                border: 2px solid #008CBA;
            }

            .btn:hover {
                background-color: #008CBA;
                color: white;
            }

        </style>
    </head>
    <body>
        <section class="container">
            <div class="one">
                <div id="thumbnailwrapper">
                    <div id="artiststhumbnail">
                        <a href="#">
                            <!--image here-->
                            <img src="http://knoesis.org/resources/images/hazardssees_logo_final.png" width="41%" alt="artist" border="1" />
                        </a>
                    </div>
                </div>
                <div id="thumbnailwrapper">
                    <h3 style="text-align: center;">Pick a Time Range</h3>
                    <div class="timepicker" style="margin-bottom: 5%;">
                        <input type="text" name="daterange" value="12-01-2015 1:30 PM - 01-30-2016 2:00 PM" />
                    </div>
                </div>
                <div id="thumbnailwrapper">
                    <form name="myForm" action="/data" method="post" onsubmit=""> 
                    <div class="radio">
                      <label><input type="radio" name="dataset" value="chennai"> Chennai<span></span></label>
                      <label><input type="radio" name="dataset" value="houston"> Houston<span></span></label>
                      <input type=submit name="btn" class="btn-style" value="submit" />
                    </div>
                    </form>
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/flooded_areas_(1).png" height="100%" alt="artist" border="1" /> &nbsp; Flooded Areas
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_help.png" height="100%" alt="artist" border="1" /> &nbsp; Medical/Rescue Help
                    Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_need_crowed_sourced.png" height="100%" alt="artist" border="1" /> &nbsp;
                    Medical/Rescue Help Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_need.png" height="100%" alt="artist" border="1" /> &nbsp; Medical/Rescue Help
                    Needed
                </div>
                
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter_available.png" height="100%" alt="artist" border="1" /> &nbsp; Shelter/Food/Supplies
                    Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter_excel_crowed_sourced.png" height="100%" alt="artist" border="1" /> &nbsp;
                    Shelter/Food/Supplies Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter.png" height="100%" alt="artist" border="1" /> &nbsp; Shelter/Food/Supplies
                    Needed
                </div>
                <!-- <div id="thumbnailwrapper">
                    <img height="20px" src="https://cdn2.iconfinder.com/data/icons/flat-style-svg-icons-part-1/512/motor_mechanic_tools-512.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Help Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/utility_infrastructure_cs.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Help Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/utility_infrastructure.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Problem
                </div> -->
                
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/siren_emergency.png" height="100%" alt="artist" border="1" /> &nbsp; Unapproachable
                    Location
                </div>
            </div>
            <div class="two">
                <div id='map'></div>
                <nav id="menu"></nav>
            </div>
        </section>
        <!-- <div id="loader"></div> -->
        <img id="loadingGif" src="/static/Preloader_3.gif" style="position:absolute; margin:auto; top:0; left:0; right:0; bottom:0;" width="100" alt="Loading">
        <div id='instructions'></div>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.21.0/moment.min.js"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/bootstrap.daterangepicker/2/daterangepicker.js"></script>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/bootstrap.daterangepicker/2/daterangepicker.css" />
        <script type="text/javascript">
        //$(document).ready(function(){
        //    $("input[type='radio']").click(function(){
        //        var radioValue = $("input[name='dataset']:checked").val();
        //        if(radioValue){
        //            console.log(radioValue);
        //        }
        //    });
            
        //});
        $('input[name="daterange"]').daterangepicker({
            timePicker: true,
            timePickerIncrement: 30,
            locale: {
                format: 'MM-DD-YYYY h:mm A'
            },
            onSelect: function () {
                $(this).change();
            }
        },function(start,end,label){
                var st = start.valueOf()
                var ed = end.valueOf()
                console.log(typeof st)
                console.log(typeof ed)
                var start_filter=['>=','uxtm',st];
                var end_filter=['<','uxtm',ed];     
                console.log(st + " " + ed)
                map.setFilter('Shelter/Food/Supplies Need',['all',start_filter,end_filter]);
                map.setFilter('Medical/Rescue Help Need',['all',start_filter,end_filter]);
                //map.setFilter('Utility/Infrastructure Problem',['all',start_filter,end_filter]);
        });        
        
        mapboxgl.accessToken = 'pk.eyJ1Ijoic2hydXRpa2FyIiwiYSI6ImNqZWVraDN3bTFiNzgyeG1rNnlvbWU5YWEifQ.3Uq8vnAz-XUAyL4YJ60l6Q'
        var map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/light-v9',
            center: ["""+",".join(str(e) for e in centroid)+"""],
            zoom: 9,
            maxZoom: 15
        });
        var months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December'
        ];
        var layers = [
            [150, '#f28cb1'],
            [20, '#f1f075'],
            [0, '#51bbd6']
        ];
        var OSM_features_icons_dict = """+OSM_features_icons_dict+""";
        // ---------------------------------------------------------------------
        map.on('load', function(e) {
            $('#loadingGif').show();
            var sd = """+shelter_data+""";
            sd.features = sd.features.map(function(d) {
                d.properties.m = new Date(d.properties.timestamp).getMinutes();
                d.properties.h = new Date(d.properties.timestamp).getHours();
                d.properties.dt = new Date(d.properties.timestamp).getDate();
                d.properties.mn = new Date(d.properties.timestamp).getMonth();
                d.properties.yr = new Date(d.properties.timestamp).getFullYear();
                d.properties.uxtm = new Date(d.properties.timestamp).getTime();
                d.properties.cls = d.properties.class;
                d.properties.num = d.properties.number;
                d.properties.lnk = d.properties.link;
                return d;
            });
            var rd = """+rescue_data+""";
            rd.features = rd.features.map(function(d) {
                d.properties.m = new Date(d.properties.timestamp).getMinutes();
                d.properties.h = new Date(d.properties.timestamp).getHours();
                d.properties.dt = new Date(d.properties.timestamp).getDate();
                d.properties.mn = new Date(d.properties.timestamp).getMonth();
                d.properties.yr = new Date(d.properties.timestamp).getFullYear();
                d.properties.uxtm = new Date(d.properties.timestamp).getTime();
                d.properties.cls = d.properties.class;
                d.properties.num = d.properties.number;
                d.properties.lnk = d.properties.link;
                return d;
            });
            
            
            map.addSource("shelter", {
                "type": "geojson",
                "data": sd
            });
            map.addSource("rescue", {
                "type": "geojson",
                "data": rd
            });
            //map.addSource("infra", {
            //    "type": "geojson",
            //    "data": ind
            //});
            
            map.addSource("osm_shelter", {
                "type": "geojson",
                "data": """+photon_shelter+"""
            });
            map.addSource("osm_rescue", {
                "type": "geojson",
                "data": """+photon_rescue+"""
            });
            
            map.addSource("heat", {
                "type": "geojson",
                "data": '/test'
            });
            map.addSource("other-shelter", {
                "type": "geojson",
                "data": """+other_sh+"""
            });
            map.addSource("other-rescue", {
                "type": "geojson",
                "data": """+other_res+"""
            });
            map.loadImage('/static/shelter.png', function(error, sh_image) {
                if (error) throw error;
                map.addImage('si', sh_image);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Need",
                    "type": "symbol",
                    "source": "shelter",
                    "layout": {
                        "icon-image": "si",
                        "icon-size": 0.7
                    },
                });
            });
            map.loadImage('/static/medical_need.png', function(error, re_image) {
                if (error) throw error;
                map.addImage('ri', re_image);
                map.addLayer({
                    "id": "Medical/Rescue Help Need",
                    "type": "symbol",
                    "source": "rescue",
                    "layout": {
                        "icon-image": "ri",
                        "icon-size": 0.7
                    },
                });
            });
            //map.loadImage('/static/utility_infrastructure.png', function(error, if_image) {
            //    if (error) throw error;
            //    map.addImage('inf', if_image);
            //    map.addLayer({
            //        "id": "Utility/Infrastructure Problem",
            //        "type": "symbol",
            //        "source": "infra",
            //        "layout": {
            //            "icon-image": "inf",
            //            "icon-size": 0.7
            //        },
            //    });
            //});
            map.loadImage('/static/shelter_available.png', function(error, o_sh) {
                if (error) throw error;
                map.addImage('osh', o_sh);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Available",
                    "type": "symbol",
                    "source": "osm_shelter",
                    "layout": {
                        "icon-image": "osh",
                        "icon-size": 0.7
                    },
                });
            });
            map.loadImage('/static/medical_help.png', function(error, o_re) {
                if (error) throw error;
                map.addImage('ore', o_re);
                map.addLayer({
                    "id": "Medical/Rescue Help Available",
                    "type": "symbol",
                    "source": "osm_rescue",
                    "layout": {
                        "icon-image": "ore",
                        "icon-size": 0.7
                    },
                });
            });
            //map.loadImage('https://cdn2.iconfinder.com/data/icons/flat-style-svg-icons-part-1/512/motor_mechanic_tools-512.png', function(error, o_inf) {
            //    if (error) throw error;
            //    map.addImage('oinf', o_inf);
            //    map.addLayer({
            //        "id": "Utility/Infrastructure Help Available",
            //        "type": "symbol",
            //        "source": "osm_infra",
            //        "layout": {
            //            "icon-image": "oinf",
            //            "icon-size": 0.05
            //        },
            //    });
            //});
            map.loadImage('/static/shelter_excel_crowed_sourced.png', function(error, oth_s) {
                if (error) throw error;
                map.addImage('oths', oth_s);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Available (CS)",
                    "type": "symbol",
                    "source": "other-shelter",
                    "layout": {
                        "icon-image": "oths",
                        "icon-size": 0.75
                    },
                });
            });
            map.loadImage('/static/medical_need_crowed_sourced.png', function(error, oth_r) {
                if (error) throw error;
                map.addImage('othr', oth_r);
                map.addLayer({
                    "id": "Medical/Rescue Help Available (CS)",
                    "type": "symbol",
                    "source": "other-rescue",
                    "layout": {
                        "icon-image": "othr",
                        "icon-size": 0.75
                    },
                });
            });
            map.addSource('trees', {
                type: 'geojson',
                data: '/test'
            });
            // add heatmap layer here
            // add circle layer here
            map.addLayer({
                id: 'Flooded Area',
                type: 'heatmap',
                source: 'trees',
                minzoom: 9,
                maxzoom: 15,
                paint: {
                    // increase weight as diameter breast height increases
                    'heatmap-weight': {
                        property: 'dbh',
                        type: 'exponential',
                        stops: [
                            [1, 0],
                            [62, 1]
                        ]
                    },
                    // increase intensity as zoom level increases
                    'heatmap-intensity': {
                        stops: [
                            [11, 1.5],
                            [15, 1.5]
                        ]
                    },
                    // assign color values be applied to points depending on their density
                    'heatmap-color': [
                        'interpolate', ['linear'],
                        ['heatmap-density'],
                        0, 'rgba(0,0,204,0)',
                        0.2, 'rgb(0,0,204)',
                        0.4, 'rgb(0,0,204)',
                        0.6, 'rgb(0,0,204)',
                        0.8, 'rgb(0,0,204)'
                    ],
                    // increase radius as zoom increases
                    'heatmap-radius': 15,
                    /*
                    'heatmap-radius': {
                        stops: [
                            [11, 15],
                            [15, 20]
                        ]
                    },*/
                    // decrease opacity to transition into the circle layer
                    'heatmap-opacity': {
                        default: 1,
                        stops: [
                            [5, 1],
                            [20, 0]
                        ]
                    },
                }
            }, 'waterway-label');
            // after done!
            $('#loadingGif').hide();
        });
        //----------------------------------------------------------------------
        var toggleableLayerIds = [ 'Shelter/Food/Supplies Need','Medical/Rescue Help Need','Shelter/Food/Supplies Available','Medical/Rescue Help Available',
                                    'Shelter/Food/Supplies Available (CS)','Medical/Rescue Help Available (CS)', 'Flooded Area'];
        for (var i = 0; i < toggleableLayerIds.length; i++) {
            var id = toggleableLayerIds[i];
            var link = document.createElement('a');
            link.href = '#';
            link.className = 'active';
            link.textContent = id;
            link.onclick = function (e) {
                var clickedLayer = this.textContent;
                e.preventDefault();
                e.stopPropagation();
                var visibility = map.getLayoutProperty(clickedLayer, 'visibility');
                if (visibility === 'visible') {
                    map.setLayoutProperty(clickedLayer, 'visibility', 'none');
                    this.className = '';
                } else {
                    this.className = 'active';
                    map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
                }
            };
            var layers = document.getElementById('menu');
            layers.appendChild(link);
        }
        // ---------------------------------------------------------------------
        var pop = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
        });
    //    map.on('mouseenter', 'Shelter/Food/Supplies Available (CS)', function(e) {
    //            map.getCanvas().style.cursor = 'pointer';
    //            var coordinates = e.features[0].geometry.coordinates.slice();
    //            var description = e.features[0].properties.description;
    //            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
    //                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    //            }
    //            pop.setLngLat(coordinates)
    //                .setHTML(description)
    //                .addTo(map);
    //        });
    //        map.on('mouseenter', 'Medical/Rescue Help Available (CS)', function(e) {
    //            map.getCanvas().style.cursor = 'pointer';
    //            var coordinates = e.features[0].geometry.coordinates.slice();
    //            var description = e.features[0].properties.description;
    //            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
    //                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    //            }
    //            pop.setLngLat(coordinates)
    //                .setHTML(description)
    //                .addTo(map);
    //        });
            map.on('mouseenter', 'Shelter/Food/Supplies Available', function(e) {
                
                map.getCanvas().style.cursor = 'pointer';
                var coordinates = e.features[0].geometry.coordinates.slice();
                description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
                description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }
                pop.setLngLat(coordinates)
                    .setHTML(description)
                    .addTo(map);
                var img = new Image();
                img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
                img.setAttribute("alt", "OSM-Icon");
                document.getElementById("img-container").appendChild(img);
                
            });
            map.on('mouseenter', 'Medical/Rescue Help Available', function(e) {
                map.getCanvas().style.cursor = 'pointer';
                var coordinates = e.features[0].geometry.coordinates.slice();
                description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
                description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }
                pop.setLngLat(coordinates)
                    .setHTML(description)
                    .addTo(map);
                var img = new Image();
                img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
                img.setAttribute("alt", "OSM-Icon");
                document.getElementById("img-container").appendChild(img);
            });
            //map.on('mouseenter', 'Utility/Infrastructure Help Available', function(e) {
            //    map.getCanvas().style.cursor = 'pointer';
            //    var coordinates = e.features[0].geometry.coordinates.slice();
            //    description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
            //    description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
            //    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            //        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            //    }
            //    pop.setLngLat(coordinates)
            //        .setHTML(description)
            //        .addTo(map);
            //    var img = new Image();
            //    img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
            //    img.setAttribute("alt", "OSM-Icon");
            //    document.getElementById("img-container").appendChild(img);
            //});
            map.on('mouseleave', 'Shelter/Food/Supplies Available (CS)', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            map.on('mouseleave', 'Medical/Rescue Help Available (CS)', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            //map.on('mouseleave', 'Utility/Infrastructure Help Available', function() {
            //    map.getCanvas().style.cursor = '';
            //    pop.remove();
            //});
            map.on('mouseleave', 'Shelter/Food/Supplies Available', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            map.on('mouseleave', 'Medical/Rescue Help Available', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
        map.on('click', function (e) {
            var features = map.queryRenderedFeatures(e.point, {layers: ['Shelter/Food/Supplies Need','Medical/Rescue Help Need']});
            if (!features.length) {
                return;
            }
            var feature = features[0];
            // Populate the popup and set its coordinates
            // based on the feature found.
            var popup = new mapboxgl.Popup()
                .setLngLat(feature.geometry.coordinates)
                .setHTML(ClickedMatchObject(feature))
                .addTo(map);
            ///HERE
            document.getElementById('btn-collectobj')
                .addEventListener('click', function(){
                    var start_cordd = feature.geometry.coordinates;
                    var cls = feature.properties.class;
                    getRoute(start_cordd,cls);
                    popup.remove();
                });
        });
        function ClickedMatchObject(feature){
            // Hide instructions if another location is chosen from the map
            $('#instructions').hide();
            var html = '';
            html += "<div>";
            html += "<fieldset class='with-icon spinner'>";
            html += "<p>" + feature.properties.description + "</p>";
            //html += "<img src='https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif' height='100%' alt='artist' border='1' />"
            //html += "<button class='btn btn-primary ' id='btn-collectobj' value='Collect'>Get Direction</button>";
            html += "<p style='text-align: center;'><input type='button' class='btn btn-primary ' id='btn-collectobj' value='&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Match Need' style='color: red; font-weight: bold; padding: 0.5em 1em; background: url(https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif) no-repeat; background-size:50% 100%;'></p>";
            html += "</fieldset>";
            html += "</div>";
            return html;
        }
        // map.on('mousemove', function (e) {
        //     var features = map.queryRenderedFeatures(e.point, {layers: ['unclustered-points']});
        //     map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';
        // });
        function getRoute(cordd, cl) {
            $('#loadingGif').show();
            var start = cordd;
            var end = [80.255722, 13.079104]; //random point. To be matched.
            $.getJSON('/find_match', {
                start_0: start[0],
                start_1: start[1],
                cl: cl
            }, function(d) {
                var end = d.end;
                var route_no = d.route_no;
                var ph = d.phone;
                if (route_no == 'not available') {
                    console.log("not available");
                    console.log(end);
                    map.loadImage('https://raw.githubusercontent.com/halolimat/FloodMapping/master/FloodMapIcons/siren_emergency.png?token=AECQADb-zk6KVJFehj9-K_0DRE-U6Nyfks5a2sl6wA%3D%3D', function(error, helip) {
                        if (error) throw error;
                        map.addImage('heli', helip);
                        map.addLayer({
                            "id": "emergency",
                            "type": "symbol",
                            source: {
                                type: 'geojson',
                                data: {
                                    type: 'Feature',
                                    geometry: {
                                        type: 'Point',
                                        coordinates: start
                                    }
                                },
                            },
                            "layout": {
                                "icon-image": "heli",
                                "icon-size": 0.75
                            },
                        });
                    });
                } else {
                    console.log(end);
                    console.log(route_no);
                    var directionsRequest = 'https://api.mapbox.com/directions/v5/mapbox/driving-traffic/' + start[0] + ',' + start[1] + ';' + end[0] + ',' + end[1] + '?overview=full&alternatives=true&steps=true&geometries=geojson&access_token=' + mapboxgl.accessToken;
                    var result = $.ajax({
                        method: 'GET',
                        url: directionsRequest,
                    }).done(function(data) {
                        console.log(data);
                        var route = data.routes[route_no].geometry;
                        
                        if (map.getLayer("route")) {
                            map.removeLayer("route");
                            map.removeSource("route");
                        }
                        map.addLayer({
                            id: 'route',
                            type: 'line',
                            source: {
                                type: 'geojson',
                                data: {
                                    type: 'Feature',
                                    geometry: route
                                }
                            },
                            paint: {
                                'line-width': 2,
                                'line-color': "blue"
                            }
                        });
                        $('#instructions').show();
                        $('instructions').html('');
                        $('instructions').empty();
                        var instructions = document.getElementById('instructions');
                        var steps = data.routes[route_no].legs[0].steps;
                        instructions.innerHTML='<p style="color:blue" >' + ph + '</p>';
                        steps.forEach(function(step) {
                            instructions.insertAdjacentHTML('beforeend', '<p>' + step.maneuver.instruction + '</p>');
                        });
                        $('#instructions').show();
                    });
                    if (map.getLayer("start")) {
                        map.removeLayer("start");
                        map.removeSource("start");
                    }
                    map.addLayer({
                        id: 'start',
                        type: 'circle',
                        source: {
                            type: 'geojson',
                            data: {
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: start
                                }
                            },
                        }
                    });
                    if (map.getLayer("end")) {
                        map.removeLayer("end");
                        map.removeSource("end");
                    }
                    map.addLayer({
                        id: 'end',
                        type: 'circle',
                        source: {
                            type: 'geojson',
                            data: {
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: end
                                }
                            },
                        }
                    });
                }
                $('#loadingGif').hide();
            });
        }
        </script>
    </body>
    </html>
"""

dname = "chennai"
geohash_fname = "_Data/"+dname+"_geohashes_8prec.json"
geohash_dict = defaultdict(bool)
if os.path.isfile(geohash_fname):
    print "returning cached file..."
    with open(geohash_fname) as f:
        geohash_dict = json.load(f)
    print len(geohash_dict.keys()), "geohashes"
else:
    print "Geohash File is not in folder"


def get_coords(lat1, lon1, lat2, lon2, amount_coords):
      return zip(np.linspace(lat1, lat2, amount_coords),
                 np.linspace(lon1, lon2, amount_coords))

def interpolate_try(crds,start):
    s_lat=start[0]
    s_lon=start[1]
    new_cord=list()
    for i in range(len(crds)):
        if i==0:
            long1 = float(s_lon)
            lat1 = float(s_lat)
            long2 = float(crds[i][0])
            lat2 = float(crds[i][1])
        elif i==(len(crds)-1):

            break
        else:

            tp=i+1
            long1 = float(crds[i][0])
            lat1 = float(crds[i][1])
            long2 = float(crds[tp][0])
            lat2 = float(crds[tp][1])
        st=list()
        ed=list()
        st.append(lat1)
        st.append(long1)
        ed.append(lat2)
        ed.append(long2)
        di=great_circle(st, ed).kilometers
        arb=di / 0.02
        # print "di",di,arb

        ass = get_coords(lat1, long1, lat2, long2, arb)

        for a in ass:
            n=list()
            n.append(a[1])
            n.append(a[0])
            new_cord.append(n)
    return new_cord


def get_dist(st,fl):
    start_ln=float(st[0])
    start_lt=float(st[1])
    points={}
    cod=list()
    R = 6373.0
    s=[]
    s.append(st[1])
    s.append(st[0])
    for i,e in enumerate(fl):

        f=[]
        f.append(e[1])
        f.append(e[0])
        distance=great_circle(s, f).kilometers
        cod.append(e)
        points[i]=distance
    # od = collections.OrderedDict(sorted(points.items()))
    sorted_x = sorted(points.items(), key=operator.itemgetter(1))
    # print sorted_x
    # for k, v in od.iteritems(): print k, v
    return sorted_x,cod

@application.route('/find_match', methods=['GET','POST'])
def find_match():
    # interpolate_try()
    start_lat = request.args.get('start_1')
    start_lon = request.args.get('start_0')
    cl = request.args.get('cl')
    if (cl=='shelter_matching'):
        d=json.loads(ph_sh)
        o=json.loads(other_s)
    if (cl=='rescue_match'):
        d=json.loads(ph_rs)
        o=json.loads(other_r)
    if (cl=='infrastructure_need'):
        d=json.loads(ph_inf)
        o=json.loads(other_i)
 
    st=list()
    st.append(start_lon)
    st.append(start_lat)
    s=list()
    s.append(start_lat)
    s.append(start_lon)
    fl=list()

    for e in d["features"]:
        # final_lon=e["geometry"]["coordinates"][0]
        # final_lat=e["geometry"]["coordinates"][1]
        final=e["geometry"]["coordinates"]
        fl.append(final)
    if o:
        for e in o["features"]:
            # final_lon=e["geometry"]["coordinates"][0]
            # final_lat=e["geometry"]["coordinates"][1]
            final=e["geometry"]["coordinates"]
            fl.append(final)

    dist=get_dist(st,fl)
    # new_dist=route_dist(st,fl)
    sorted_dist=dist[0]
    new_cord=dist[1]
    final_route=None

    end=list()
    route_no = ""

    for i in range(len(sorted_dist)):
        index=sorted_dist[i][0]
        new_lon= new_cord[index][0]
        new_lat= new_cord[index][1]
        response=requests.get("https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"+str(start_lon)+","+str(start_lat)+";"+str(new_lon)+","+str(new_lat)+"?geometries=geojson&access_token=pk.eyJ1IjoiaGFsb2xpbWF0IiwiYSI6ImNqZWRrcjM2bTFrcWEzMmxucDQ4N2kxaDMifQ.Buarvvdqz7yJ1O25up2SzA")
        all_data=json.loads(response.content)
        # print i,all_data
        try:
            for r in range(len(all_data['routes'])):
                route = all_data['routes'][r]['geometry']
                all_cords = route['coordinates']

                res = flood_check(all_cords,s)
                if res == "flooded route":
                    continue
                if res == "route safe":
                    end.append(new_lon)
                    end.append(new_lat)
                    final_route=route
                    route_no=r
            if final_route is None:
                continue
            else:
                break
        except:
            end.append(start_lon)
            end.append(start_lat)
            route_no="not available"
            break
    new_name=""
    if route_no!="not available":
        for e in d["features"]:
            if e["geometry"]["coordinates"]==end:
                new_name=e["properties"]["name"]
                # print new_name
                break
    if new_name=="":
        j= json.dumps({"end":end,"route_no":route_no,"phone":"not available"});
    else:
        try:
            new_lon=end[0]
            new_lat=end[1]
            response1=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(new_lat)+","+str(new_lon)+"&radius=500&keyword="+new_name+"&key=AIzaSyANUmhGp9RnNMVg4yZCIF-P0lMovGbTNEg")
            all_data1=json.loads(response1.content)
            place_id=all_data1["results"][0]["place_id"]
            response=requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid="+place_id+"&key=AIzaSyANUmhGp9RnNMVg4yZCIF-P0lMovGbTNEg")
            all_data=json.loads(response.content)
            phone_numb= all_data["result"]["formatted_phone_number"]
            address=all_data["result"]["formatted_address"]
            all_data=new_name+","+"contact information : "+address+" "+str(phone_numb)
        except:
            all_data="not available"
        j= json.dumps({"end":end,"route_no":route_no,"phone":all_data});


    # print j
    return j

def flood_check(cordin,strt):
    # print len(cordin)
    cordin = interpolate_try(cordin,strt)
    # print cordin
    # print len(cordin)
    f=None
    for e in cordin:
        # print e
        ln=e[0]
        lt = e[1]
        # print type(ln),lt
        f=None
        n_end=list()
        n_end.append(lt)
        n_end.append(ln)
        dis=great_circle(strt, n_end).kilometers
        geohash = Geohash.encode(ln,lt, precision=8)
        if geohash_dict.get(geohash) is not None:
            x=geohash_dict[geohash]
        else:
            x="No Satellite Data!"
        # print x
        if str(x)=="True" and dis>0.5:
            # print "entered true"
            f="flooded route"
            break
    # print f
    if f=="flooded route":
        return f
    else:
        return "route safe"

@application.route("/data", methods=['GET','POST'])
def get_data():
    dataset = request.form['dataset']
    read_data(dataset)
    map_ = index(dataset)
    return map_


def read_data(dataset):
# dataset="houston"
    # dataset=request.args.get('dataset')
    global sh,rs,inf,ph_sh,ph_rs,ph_inf,other_s,other_r,other_i,centroid

    if dataset=="houston":
        centroid=[-95.3635526899414,29.759425736966094]
    elif dataset=="chennai":
        centroid=[80.21378369330633,13.018400446841508]

    r = requests.get('http://localhost:9200')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    s=[]
    for i in range(9000):
        try:
            s.append(es.get(index=dataset+'-tweets', doc_type='people', id=i)["_source"])
        except:
            break
    # print s

    p=[]
    for c in range(9000):
        try:
            p.append(es.get(index=dataset+'1', doc_type='locs', id=c)["_source"])
        except:
            break

    crowd=[]
    for c in range(9000):
        try:
            crowd.append(es.get(index=dataset+'-crowd', doc_type='crowd', id=c)["_source"])
        except:
            break

    shelter=list()
    rescue=list()
    infra=list()
    for e in s:
        if e["properties"]["class"]=="shelter_matching":
            shelter.append(e)
        elif e["properties"]["class"]=="rescue_match":
            rescue.append(e)
        else:
            infra.append(e)
    sh=str(json.dumps({"type": "FeatureCollection", "features": shelter}))
    rs=str(json.dumps({"type": "FeatureCollection", "features": rescue}))
    inf=str(json.dumps({"type": "FeatureCollection", "features": infra}))
    ph_shelter=list()
    ph_rescue=list()
    ph_infra=list()
    for e in p:
        if e["properties"]["class"]=="shelter_matching" and e["properties"]["Flood"]=='False':
            ph_shelter.append(e)
        elif e["properties"]["class"]=="rescue_match" and e["properties"]["Flood"]=='False':
            ph_rescue.append(e)
        elif e["properties"]["class"]=="infrastructure_need" and e["properties"]["Flood"]=='False':
            ph_infra.append(e)
    ph_sh=str(json.dumps({"type": "FeatureCollection", "features": ph_shelter}))
    ph_rs=str(json.dumps({"type": "FeatureCollection", "features": ph_rescue}))
    ph_inf=str(json.dumps({"type": "FeatureCollection", "features": ph_infra}))
    other_shelter=list()
    other_rescue=list()
    other_infra=list()
    for e in crowd:
        if e["properties"]["class"]=="shelter_matching" and e["properties"]["Flood"]=='False':
            other_shelter.append(e)
        elif e["properties"]["class"]=="rescue_match" and e["properties"]["Flood"]=='False':
            other_rescue.append(e)
        elif e["properties"]["class"]=="infrastructure_need" and e["properties"]["Flood"]=='False':
            other_infra.append(e)
    other_s=str(json.dumps({"type": "FeatureCollection", "features": other_shelter}))
    other_r=str(json.dumps({"type": "FeatureCollection", "features": other_rescue}))
    other_i=str(json.dumps({"type": "FeatureCollection", "features": other_infra}))


@application.route("/<gaz_name>")
def index(gaz_name):
    if gaz_name not in ["chennai","houston"]:
        options = """
            <p> </p>
        """
        return options
    
    gaz_name=gaz_name.lower()
    # print "came to index"

    read_data(gaz_name)

    map = make_map( centroid=centroid,
                    shelter_data=sh,
                    rescue_data=rs,
                    photon_shelter=ph_sh,
                    photon_rescue=ph_rs,
                    other_sh=other_s,
                    other_res=other_r)

    return map


@application.route('/test', methods=['GET','POST'])
def check_selected():
    with open("_Data/chennai.geojson") as f:
        data = json.load(f)
    data["features"] = data["features"][0::3]
    return json.dumps(data)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8088)
    # interpolate_try()
    # intp() 

Location
Rescue
Flood mapping
Directions
Disaster mapping
Routing
Matching
Disaster Response
Social Media
"""


def make_map(centroid,shelter_data,rescue_data,photon_shelter,photon_rescue,other_sh,other_res):

    with open("_Data/OSM_features_icons_dict.json") as f:
        OSM_features_icons_dict = json.dumps(json.load(f))

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8' />
        <title></title>
        <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
        <script src='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.js'></script>
        <link href='https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css' rel='stylesheet' />
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/bootstrap/3/css/bootstrap.css" />
        <style>
            body, html{
                height: 100%;
                width : 100%;
                padding: 0;
            }
            body{
                background-color: #CAD2D3;
            }
            .container {
                width: 100%;
                //padding: 10px;
                height: 100%
            }
            .one {
                float: left;
                height: 100%;
                width : 24%;
                padding-top: 10px;
                margin-left: -4px;
            }
            .two {
                margin-left: 10%;
                height: 100%;
                width: 80%;
            }
            #map {  position:absolute;
                    top:0; bottom:0; width:75%; transition: all 0.3s; margin-left: 14%;}
            .button { color: #fff; background-color: #555; padding: 1em; margin: 1em; position: absolute; right: 1em; top: 1em; border-radius: 0.5em; border-bottom: 2px #222 solid; cursor: pointer; }
            #resizeMap { top: 5em; }
            #instructions {
                position: absolute;
                margin-left: 30%;
                margin-top: 30%;
                height: 30%;
                width: 20%;
                top: 0;
                bottom: 0;
                padding: 10px;
                background-color: rgba(202,210,211, 0.7);
                overflow-y: scroll;
                display: none;
                color: rgb(0,63,121);
            }
            .map-overlay {
                font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
                position: absolute;
                width: 25%;
                top: 0;
                left: 0;
                padding: 10px;
            }
            .popup {
                position: relative;
                display: inline-block;
                cursor: pointer;
            }
            .popup .popuptext {
                visibility: hidden;
                width: 160px;
                background-color: #555;
                color: #fff;
                text-align: center;
                border-radius: 6px;
                padding: 8px 0;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -80px;
            }
            .popup .popuptext::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #555 transparent transparent transparent;
            }
            .popup .show {
                visibility: visible;
                -webkit-animation: fadeIn 1s;
                animation: fadeIn 1s
            }
            /* Add animation (fade in the popup) */
            @-webkit-keyframes fadeIn {
                from {opacity: 0;}
                to {opacity: 1;}
            }
            @keyframes fadeIn {
                from {opacity: 0;}
                to {opacity:1 ;}
            }
            input[type=text] {
                background-color: transparent;
                color: black;
                //border: 2px solid white;
                border-radius: 4px;
                width: 100%;
            }
            input[type=text]:focus {
                background-color: lightblue;
                color: black;
                border: 2px solid white;
                border-radius: 4px;
            }
            .mapboxgl-popup {
                max-width: 400px;
                font: 12px/20px 'Helvetica Neue', Arial, Helvetica, sans-serif;
            }
            #thumbnailwrapper {
                color:#2A2A2A;margin-right:5px;
                border-radius:0.2em;
                margin-bottom:5px;
                background-color:white;
                padding:5px;
                //border-color:#DADADA;
                border-style:solid;
                border-width:thin;
                font-size:15px
                text-align: center;
            }
            #thumbnailwrapper:hover{box-shadow:0 0 5px 5px #DDDDDD}
            #artiststhumbnail {
                width:100%;
                height:25%;
                overflow:hidden;
                //border-color:#DADADA;
                //border-style:solid;
                border-width:thin;
                //background-color:gray;
            }
            #artiststhumbnail:hover {left:50px }
            #genre {
                font-size:12px;
                font-weight:bold;
                color:#2A2A2A
            }
            #artiststhumbnail a img {
                display : block;
                margin : auto;
            }
            #loading {
                //position: absolute;
                width: 75%; height: 100%; background: url('/static/Preloader_3.gif') no-repeat center center;
            }
            #loader {
                float: left;
                position:absolute;
                height:100%;
                width:100%;
                background:gray;
                -ms-opacity:0.5;
                opacity:0.5;
                //z-index:1000000;
                display: none;
                //margin-left: -40px;
                //margin-top: -19px;
            }
            #menu {
                background: #fff;
                position: absolute;
                z-index: 1;
                top: 10px;
                right: 10px;
                border-radius: 3px;
                width: 120px;
                border: 1px solid rgba(0,0,0,0.4);
                font-family: 'Open Sans', sans-serif;
            }
            #menu a {
                font-size: 13px;
                color: #404040;
                display: block;
                margin: 0;
                padding: 0;
                padding: 10px;
                text-decoration: none;
                border-bottom: 1px solid rgba(0,0,0,0.25);
                text-align: center;
            }
            #menu a:last-child {
                border: none;
            }
            #menu a:hover {
                background-color: #f8f8f8;
                color: #404040;
            }
            #menu a.active {
                background-color: #3887be;
                color: #ffffff;
            }
            #menu a.active:hover {
                background: #3074a4;
            }
            .radio input[type='radio'] {
              display: none;
              /*removes original button*/
            }

            .radio label:before {
              /*styles outer circle*/
              content: " ";
              display: inline-block;
              position: relative;
              top: 5px;
              margin: 0 5px 0 0;
              width: 20px;
              height: 20px;
              border-radius: 11px;
              border: 2px solid orange;
              background-color: transparent;
            }

            .radio label {
              position: relative;
            }

            .radio label input[type='radio']:checked+span {
              /*styles inside circle*/
              border-radius: 11px;
              width: 12px;
              height: 12px;
              position: absolute;
              top: 9px;
              left: 24px;
              display: block;
              background-color: blue;
            }
            

            .btn {
                background-color: white; 
                color: black; 
                border: 2px solid #008CBA;
            }

            .btn:hover {
                background-color: #008CBA;
                color: white;
            }

        </style>
    </head>
    <body>
        <section class="container">
            <div class="one">
                <div id="thumbnailwrapper">
                    <div id="artiststhumbnail">
                        <a href="#">
                            <!--image here-->
                            <img src="http://knoesis.org/resources/images/hazardssees_logo_final.png" width="41%" alt="artist" border="1" />
                        </a>
                    </div>
                </div>
                <div id="thumbnailwrapper">
                    <h3 style="text-align: center;">Pick a Time Range</h3>
                    <div class="timepicker" style="margin-bottom: 5%;">
                        <input type="text" name="daterange" value="12-01-2015 1:30 PM - 01-30-2016 2:00 PM" />
                    </div>
                </div>
                <div id="thumbnailwrapper">
                    <form name="myForm" action="/data" method="post" onsubmit=""> 
                    <div class="radio">
                      <label><input type="radio" name="dataset" value="chennai"> Chennai<span></span></label>
                      <label><input type="radio" name="dataset" value="houston"> Houston<span></span></label>
                      <input type=submit name="btn" class="btn-style" value="submit" />
                    </div>
                    </form>
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/flooded_areas_(1).png" height="100%" alt="artist" border="1" /> &nbsp; Flooded Areas
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_help.png" height="100%" alt="artist" border="1" /> &nbsp; Medical/Rescue Help
                    Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_need_crowed_sourced.png" height="100%" alt="artist" border="1" /> &nbsp;
                    Medical/Rescue Help Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/medical_need.png" height="100%" alt="artist" border="1" /> &nbsp; Medical/Rescue Help
                    Needed
                </div>
                
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter_available.png" height="100%" alt="artist" border="1" /> &nbsp; Shelter/Food/Supplies
                    Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter_excel_crowed_sourced.png" height="100%" alt="artist" border="1" /> &nbsp;
                    Shelter/Food/Supplies Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/shelter.png" height="100%" alt="artist" border="1" /> &nbsp; Shelter/Food/Supplies
                    Needed
                </div>
                <!-- <div id="thumbnailwrapper">
                    <img height="20px" src="https://cdn2.iconfinder.com/data/icons/flat-style-svg-icons-part-1/512/motor_mechanic_tools-512.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Help Available
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/utility_infrastructure_cs.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Help Available (CS)
                </div>
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/utility_infrastructure.png" height="100%" alt="artist" border="1" /> &nbsp; Utility/Infrastructure Problem
                </div> -->
                
                <div id="thumbnailwrapper">
                    <img height="20px" src="/static/siren_emergency.png" height="100%" alt="artist" border="1" /> &nbsp; Unapproachable
                    Location
                </div>
            </div>
            <div class="two">
                <div id='map'></div>
                <nav id="menu"></nav>
            </div>
        </section>
        <!-- <div id="loader"></div> -->
        <img id="loadingGif" src="/static/Preloader_3.gif" style="position:absolute; margin:auto; top:0; left:0; right:0; bottom:0;" width="100" alt="Loading">
        <div id='instructions'></div>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.21.0/moment.min.js"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/bootstrap.daterangepicker/2/daterangepicker.js"></script>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/bootstrap.daterangepicker/2/daterangepicker.css" />
        <script type="text/javascript">
        //$(document).ready(function(){
        //    $("input[type='radio']").click(function(){
        //        var radioValue = $("input[name='dataset']:checked").val();
        //        if(radioValue){
        //            console.log(radioValue);
        //        }
        //    });
            
        //});
        $('input[name="daterange"]').daterangepicker({
            timePicker: true,
            timePickerIncrement: 30,
            locale: {
                format: 'MM-DD-YYYY h:mm A'
            },
            onSelect: function () {
                $(this).change();
            }
        },function(start,end,label){
                var st = start.valueOf()
                var ed = end.valueOf()
                console.log(typeof st)
                console.log(typeof ed)
                var start_filter=['>=','uxtm',st];
                var end_filter=['<','uxtm',ed];     
                console.log(st + " " + ed)
                map.setFilter('Shelter/Food/Supplies Need',['all',start_filter,end_filter]);
                map.setFilter('Medical/Rescue Help Need',['all',start_filter,end_filter]);
                //map.setFilter('Utility/Infrastructure Problem',['all',start_filter,end_filter]);
        });        
        
        mapboxgl.accessToken = 'pk.eyJ1Ijoic2hydXRpa2FyIiwiYSI6ImNqZWVraDN3bTFiNzgyeG1rNnlvbWU5YWEifQ.3Uq8vnAz-XUAyL4YJ60l6Q'
        var map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/light-v9',
            center: ["""+",".join(str(e) for e in centroid)+"""],
            zoom: 9,
            maxZoom: 15
        });
        var months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December'
        ];
        var layers = [
            [150, '#f28cb1'],
            [20, '#f1f075'],
            [0, '#51bbd6']
        ];
        var OSM_features_icons_dict = """+OSM_features_icons_dict+""";
        // ---------------------------------------------------------------------
        map.on('load', function(e) {
            $('#loadingGif').show();
            var sd = """+shelter_data+""";
            sd.features = sd.features.map(function(d) {
                d.properties.m = new Date(d.properties.timestamp).getMinutes();
                d.properties.h = new Date(d.properties.timestamp).getHours();
                d.properties.dt = new Date(d.properties.timestamp).getDate();
                d.properties.mn = new Date(d.properties.timestamp).getMonth();
                d.properties.yr = new Date(d.properties.timestamp).getFullYear();
                d.properties.uxtm = new Date(d.properties.timestamp).getTime();
                d.properties.cls = d.properties.class;
                d.properties.num = d.properties.number;
                d.properties.lnk = d.properties.link;
                return d;
            });
            var rd = """+rescue_data+""";
            rd.features = rd.features.map(function(d) {
                d.properties.m = new Date(d.properties.timestamp).getMinutes();
                d.properties.h = new Date(d.properties.timestamp).getHours();
                d.properties.dt = new Date(d.properties.timestamp).getDate();
                d.properties.mn = new Date(d.properties.timestamp).getMonth();
                d.properties.yr = new Date(d.properties.timestamp).getFullYear();
                d.properties.uxtm = new Date(d.properties.timestamp).getTime();
                d.properties.cls = d.properties.class;
                d.properties.num = d.properties.number;
                d.properties.lnk = d.properties.link;
                return d;
            });
            
            
            map.addSource("shelter", {
                "type": "geojson",
                "data": sd
            });
            map.addSource("rescue", {
                "type": "geojson",
                "data": rd
            });
            //map.addSource("infra", {
            //    "type": "geojson",
            //    "data": ind
            //});
            
            map.addSource("osm_shelter", {
                "type": "geojson",
                "data": """+photon_shelter+"""
            });
            map.addSource("osm_rescue", {
                "type": "geojson",
                "data": """+photon_rescue+"""
            });
            
            map.addSource("heat", {
                "type": "geojson",
                "data": '/test'
            });
            map.addSource("other-shelter", {
                "type": "geojson",
                "data": """+other_sh+"""
            });
            map.addSource("other-rescue", {
                "type": "geojson",
                "data": """+other_res+"""
            });
            map.loadImage('/static/shelter.png', function(error, sh_image) {
                if (error) throw error;
                map.addImage('si', sh_image);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Need",
                    "type": "symbol",
                    "source": "shelter",
                    "layout": {
                        "icon-image": "si",
                        "icon-size": 0.7
                    },
                });
            });
            map.loadImage('/static/medical_need.png', function(error, re_image) {
                if (error) throw error;
                map.addImage('ri', re_image);
                map.addLayer({
                    "id": "Medical/Rescue Help Need",
                    "type": "symbol",
                    "source": "rescue",
                    "layout": {
                        "icon-image": "ri",
                        "icon-size": 0.7
                    },
                });
            });
            //map.loadImage('/static/utility_infrastructure.png', function(error, if_image) {
            //    if (error) throw error;
            //    map.addImage('inf', if_image);
            //    map.addLayer({
            //        "id": "Utility/Infrastructure Problem",
            //        "type": "symbol",
            //        "source": "infra",
            //        "layout": {
            //            "icon-image": "inf",
            //            "icon-size": 0.7
            //        },
            //    });
            //});
            map.loadImage('/static/shelter_available.png', function(error, o_sh) {
                if (error) throw error;
                map.addImage('osh', o_sh);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Available",
                    "type": "symbol",
                    "source": "osm_shelter",
                    "layout": {
                        "icon-image": "osh",
                        "icon-size": 0.7
                    },
                });
            });
            map.loadImage('/static/medical_help.png', function(error, o_re) {
                if (error) throw error;
                map.addImage('ore', o_re);
                map.addLayer({
                    "id": "Medical/Rescue Help Available",
                    "type": "symbol",
                    "source": "osm_rescue",
                    "layout": {
                        "icon-image": "ore",
                        "icon-size": 0.7
                    },
                });
            });
            //map.loadImage('https://cdn2.iconfinder.com/data/icons/flat-style-svg-icons-part-1/512/motor_mechanic_tools-512.png', function(error, o_inf) {
            //    if (error) throw error;
            //    map.addImage('oinf', o_inf);
            //    map.addLayer({
            //        "id": "Utility/Infrastructure Help Available",
            //        "type": "symbol",
            //        "source": "osm_infra",
            //        "layout": {
            //            "icon-image": "oinf",
            //            "icon-size": 0.05
            //        },
            //    });
            //});
            map.loadImage('/static/shelter_excel_crowed_sourced.png', function(error, oth_s) {
                if (error) throw error;
                map.addImage('oths', oth_s);
                map.addLayer({
                    "id": "Shelter/Food/Supplies Available (CS)",
                    "type": "symbol",
                    "source": "other-shelter",
                    "layout": {
                        "icon-image": "oths",
                        "icon-size": 0.75
                    },
                });
            });
            map.loadImage('/static/medical_need_crowed_sourced.png', function(error, oth_r) {
                if (error) throw error;
                map.addImage('othr', oth_r);
                map.addLayer({
                    "id": "Medical/Rescue Help Available (CS)",
                    "type": "symbol",
                    "source": "other-rescue",
                    "layout": {
                        "icon-image": "othr",
                        "icon-size": 0.75
                    },
                });
            });
            map.addSource('trees', {
                type: 'geojson',
                data: '/test'
            });
            // add heatmap layer here
            // add circle layer here
            map.addLayer({
                id: 'Flooded Area',
                type: 'heatmap',
                source: 'trees',
                minzoom: 9,
                maxzoom: 15,
                paint: {
                    // increase weight as diameter breast height increases
                    'heatmap-weight': {
                        property: 'dbh',
                        type: 'exponential',
                        stops: [
                            [1, 0],
                            [62, 1]
                        ]
                    },
                    // increase intensity as zoom level increases
                    'heatmap-intensity': {
                        stops: [
                            [11, 1.5],
                            [15, 1.5]
                        ]
                    },
                    // assign color values be applied to points depending on their density
                    'heatmap-color': [
                        'interpolate', ['linear'],
                        ['heatmap-density'],
                        0, 'rgba(0,0,204,0)',
                        0.2, 'rgb(0,0,204)',
                        0.4, 'rgb(0,0,204)',
                        0.6, 'rgb(0,0,204)',
                        0.8, 'rgb(0,0,204)'
                    ],
                    // increase radius as zoom increases
                    'heatmap-radius': 15,
                    /*
                    'heatmap-radius': {
                        stops: [
                            [11, 15],
                            [15, 20]
                        ]
                    },*/
                    // decrease opacity to transition into the circle layer
                    'heatmap-opacity': {
                        default: 1,
                        stops: [
                            [5, 1],
                            [20, 0]
                        ]
                    },
                }
            }, 'waterway-label');
            // after done!
            $('#loadingGif').hide();
        });
        //----------------------------------------------------------------------
        var toggleableLayerIds = [ 'Shelter/Food/Supplies Need','Medical/Rescue Help Need','Shelter/Food/Supplies Available','Medical/Rescue Help Available',
                                    'Shelter/Food/Supplies Available (CS)','Medical/Rescue Help Available (CS)', 'Flooded Area'];
        for (var i = 0; i < toggleableLayerIds.length; i++) {
            var id = toggleableLayerIds[i];
            var link = document.createElement('a');
            link.href = '#';
            link.className = 'active';
            link.textContent = id;
            link.onclick = function (e) {
                var clickedLayer = this.textContent;
                e.preventDefault();
                e.stopPropagation();
                var visibility = map.getLayoutProperty(clickedLayer, 'visibility');
                if (visibility === 'visible') {
                    map.setLayoutProperty(clickedLayer, 'visibility', 'none');
                    this.className = '';
                } else {
                    this.className = 'active';
                    map.setLayoutProperty(clickedLayer, 'visibility', 'visible');
                }
            };
            var layers = document.getElementById('menu');
            layers.appendChild(link);
        }
        // ---------------------------------------------------------------------
        var pop = new mapboxgl.Popup({
                closeButton: false,
                closeOnClick: false
        });
    //    map.on('mouseenter', 'Shelter/Food/Supplies Available (CS)', function(e) {
    //            map.getCanvas().style.cursor = 'pointer';
    //            var coordinates = e.features[0].geometry.coordinates.slice();
    //            var description = e.features[0].properties.description;
    //            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
    //                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    //            }
    //            pop.setLngLat(coordinates)
    //                .setHTML(description)
    //                .addTo(map);
    //        });
    //        map.on('mouseenter', 'Medical/Rescue Help Available (CS)', function(e) {
    //            map.getCanvas().style.cursor = 'pointer';
    //            var coordinates = e.features[0].geometry.coordinates.slice();
    //            var description = e.features[0].properties.description;
    //            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
    //                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    //            }
    //            pop.setLngLat(coordinates)
    //                .setHTML(description)
    //                .addTo(map);
    //        });
            map.on('mouseenter', 'Shelter/Food/Supplies Available', function(e) {
                
                map.getCanvas().style.cursor = 'pointer';
                var coordinates = e.features[0].geometry.coordinates.slice();
                description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
                description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }
                pop.setLngLat(coordinates)
                    .setHTML(description)
                    .addTo(map);
                var img = new Image();
                img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
                img.setAttribute("alt", "OSM-Icon");
                document.getElementById("img-container").appendChild(img);
                
            });
            map.on('mouseenter', 'Medical/Rescue Help Available', function(e) {
                map.getCanvas().style.cursor = 'pointer';
                var coordinates = e.features[0].geometry.coordinates.slice();
                description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
                description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                }
                pop.setLngLat(coordinates)
                    .setHTML(description)
                    .addTo(map);
                var img = new Image();
                img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
                img.setAttribute("alt", "OSM-Icon");
                document.getElementById("img-container").appendChild(img);
            });
            //map.on('mouseenter', 'Utility/Infrastructure Help Available', function(e) {
            //    map.getCanvas().style.cursor = 'pointer';
            //    var coordinates = e.features[0].geometry.coordinates.slice();
            //    description ="<table><tr><th><div class='banner-section' id='img-container' style='float:left'></div></th>";
            //    description += "<th style='padding: 10px'>"+e.features[0].properties.name+"</th></tr></table>";
            //    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
            //        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
            //    }
            //    pop.setLngLat(coordinates)
            //        .setHTML(description)
            //        .addTo(map);
            //    var img = new Image();
            //    img.src = OSM_features_icons_dict[e.features[0].properties.key][e.features[0].properties.value];
            //    img.setAttribute("alt", "OSM-Icon");
            //    document.getElementById("img-container").appendChild(img);
            //});
            map.on('mouseleave', 'Shelter/Food/Supplies Available (CS)', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            map.on('mouseleave', 'Medical/Rescue Help Available (CS)', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            //map.on('mouseleave', 'Utility/Infrastructure Help Available', function() {
            //    map.getCanvas().style.cursor = '';
            //    pop.remove();
            //});
            map.on('mouseleave', 'Shelter/Food/Supplies Available', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
            map.on('mouseleave', 'Medical/Rescue Help Available', function() {
                map.getCanvas().style.cursor = '';
                pop.remove();
            });
        map.on('click', function (e) {
            var features = map.queryRenderedFeatures(e.point, {layers: ['Shelter/Food/Supplies Need','Medical/Rescue Help Need']});
            if (!features.length) {
                return;
            }
            var feature = features[0];
            // Populate the popup and set its coordinates
            // based on the feature found.
            var popup = new mapboxgl.Popup()
                .setLngLat(feature.geometry.coordinates)
                .setHTML(ClickedMatchObject(feature))
                .addTo(map);
            ///HERE
            document.getElementById('btn-collectobj')
                .addEventListener('click', function(){
                    var start_cordd = feature.geometry.coordinates;
                    var cls = feature.properties.class;
                    getRoute(start_cordd,cls);
                    popup.remove();
                });
        });
        function ClickedMatchObject(feature){
            // Hide instructions if another location is chosen from the map
            $('#instructions').hide();
            var html = '';
            html += "<div>";
            html += "<fieldset class='with-icon spinner'>";
            html += "<p>" + feature.properties.description + "</p>";
            //html += "<img src='https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif' height='100%' alt='artist' border='1' />"
            //html += "<button class='btn btn-primary ' id='btn-collectobj' value='Collect'>Get Direction</button>";
            html += "<p style='text-align: center;'><input type='button' class='btn btn-primary ' id='btn-collectobj' value='&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Match Need' style='color: red; font-weight: bold; padding: 0.5em 1em; background: url(https://digitalsynopsis.com/wp-content/uploads/2016/06/loading-animations-preloader-gifs-ui-ux-effects-10.gif) no-repeat; background-size:50% 100%;'></p>";
            html += "</fieldset>";
            html += "</div>";
            return html;
        }
        // map.on('mousemove', function (e) {
        //     var features = map.queryRenderedFeatures(e.point, {layers: ['unclustered-points']});
        //     map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';
        // });
        function getRoute(cordd, cl) {
            $('#loadingGif').show();
            var start = cordd;
            var end = [80.255722, 13.079104]; //random point. To be matched.
            $.getJSON('/find_match', {
                start_0: start[0],
                start_1: start[1],
                cl: cl
            }, function(d) {
                var end = d.end;
                var route_no = d.route_no;
                var ph = d.phone;
                if (route_no == 'not available') {
                    console.log("not available");
                    console.log(end);
                    map.loadImage('https://raw.githubusercontent.com/halolimat/FloodMapping/master/FloodMapIcons/siren_emergency.png?token=AECQADb-zk6KVJFehj9-K_0DRE-U6Nyfks5a2sl6wA%3D%3D', function(error, helip) {
                        if (error) throw error;
                        map.addImage('heli', helip);
                        map.addLayer({
                            "id": "emergency",
                            "type": "symbol",
                            source: {
                                type: 'geojson',
                                data: {
                                    type: 'Feature',
                                    geometry: {
                                        type: 'Point',
                                        coordinates: start
                                    }
                                },
                            },
                            "layout": {
                                "icon-image": "heli",
                                "icon-size": 0.75
                            },
                        });
                    });
                } else {
                    console.log(end);
                    console.log(route_no);
                    var directionsRequest = 'https://api.mapbox.com/directions/v5/mapbox/driving-traffic/' + start[0] + ',' + start[1] + ';' + end[0] + ',' + end[1] + '?overview=full&alternatives=true&steps=true&geometries=geojson&access_token=' + mapboxgl.accessToken;
                    var result = $.ajax({
                        method: 'GET',
                        url: directionsRequest,
                    }).done(function(data) {
                        console.log(data);
                        var route = data.routes[route_no].geometry;
                        
                        if (map.getLayer("route")) {
                            map.removeLayer("route");
                            map.removeSource("route");
                        }
                        map.addLayer({
                            id: 'route',
                            type: 'line',
                            source: {
                                type: 'geojson',
                                data: {
                                    type: 'Feature',
                                    geometry: route
                                }
                            },
                            paint: {
                                'line-width': 2,
                                'line-color': "blue"
                            }
                        });
                        $('#instructions').show();
                        $('instructions').html('');
                        $('instructions').empty();
                        var instructions = document.getElementById('instructions');
                        var steps = data.routes[route_no].legs[0].steps;
                        instructions.innerHTML='<p style="color:blue" >' + ph + '</p>';
                        steps.forEach(function(step) {
                            instructions.insertAdjacentHTML('beforeend', '<p>' + step.maneuver.instruction + '</p>');
                        });
                        $('#instructions').show();
                    });
                    if (map.getLayer("start")) {
                        map.removeLayer("start");
                        map.removeSource("start");
                    }
                    map.addLayer({
                        id: 'start',
                        type: 'circle',
                        source: {
                            type: 'geojson',
                            data: {
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: start
                                }
                            },
                        }
                    });
                    if (map.getLayer("end")) {
                        map.removeLayer("end");
                        map.removeSource("end");
                    }
                    map.addLayer({
                        id: 'end',
                        type: 'circle',
                        source: {
                            type: 'geojson',
                            data: {
                                type: 'Feature',
                                geometry: {
                                    type: 'Point',
                                    coordinates: end
                                }
                            },
                        }
                    });
                }
                $('#loadingGif').hide();
            });
        }
        </script>
    </body>
    </html>
"""

dname = "chennai"
geohash_fname = "_Data/"+dname+"_geohashes_8prec.json"
geohash_dict = defaultdict(bool)
if os.path.isfile(geohash_fname):
    print "returning cached file..."
    with open(geohash_fname) as f:
        geohash_dict = json.load(f)
    print len(geohash_dict.keys()), "geohashes"
else:
    print "Geohash File is not in folder"


def get_coords(lat1, lon1, lat2, lon2, amount_coords):
      return zip(np.linspace(lat1, lat2, amount_coords),
                 np.linspace(lon1, lon2, amount_coords))

def interpolate_try(crds,start):
    s_lat=start[0]
    s_lon=start[1]
    new_cord=list()
    for i in range(len(crds)):
        if i==0:
            long1 = float(s_lon)
            lat1 = float(s_lat)
            long2 = float(crds[i][0])
            lat2 = float(crds[i][1])
        elif i==(len(crds)-1):

            break
        else:

            tp=i+1
            long1 = float(crds[i][0])
            lat1 = float(crds[i][1])
            long2 = float(crds[tp][0])
            lat2 = float(crds[tp][1])
        st=list()
        ed=list()
        st.append(lat1)
        st.append(long1)
        ed.append(lat2)
        ed.append(long2)
        di=great_circle(st, ed).kilometers
        arb=di / 0.02
        # print "di",di,arb

        ass = get_coords(lat1, long1, lat2, long2, arb)

        for a in ass:
            n=list()
            n.append(a[1])
            n.append(a[0])
            new_cord.append(n)
    return new_cord


def get_dist(st,fl):
    start_ln=float(st[0])
    start_lt=float(st[1])
    points={}
    cod=list()
    R = 6373.0
    s=[]
    s.append(st[1])
    s.append(st[0])
    for i,e in enumerate(fl):

        f=[]
        f.append(e[1])
        f.append(e[0])
        distance=great_circle(s, f).kilometers
        cod.append(e)
        points[i]=distance
    # od = collections.OrderedDict(sorted(points.items()))
    sorted_x = sorted(points.items(), key=operator.itemgetter(1))
    # print sorted_x
    # for k, v in od.iteritems(): print k, v
    return sorted_x,cod

@application.route('/find_match', methods=['GET','POST'])
def find_match():
    # interpolate_try()
    start_lat = request.args.get('start_1')
    start_lon = request.args.get('start_0')
    cl = request.args.get('cl')
    if (cl=='shelter_matching'):
        d=json.loads(ph_sh)
        o=json.loads(other_s)
    if (cl=='rescue_match'):
        d=json.loads(ph_rs)
        o=json.loads(other_r)
    if (cl=='infrastructure_need'):
        d=json.loads(ph_inf)
        o=json.loads(other_i)
 
    st=list()
    st.append(start_lon)
    st.append(start_lat)
    s=list()
    s.append(start_lat)
    s.append(start_lon)
    fl=list()

    for e in d["features"]:
        # final_lon=e["geometry"]["coordinates"][0]
        # final_lat=e["geometry"]["coordinates"][1]
        final=e["geometry"]["coordinates"]
        fl.append(final)
    if o:
        for e in o["features"]:
            # final_lon=e["geometry"]["coordinates"][0]
            # final_lat=e["geometry"]["coordinates"][1]
            final=e["geometry"]["coordinates"]
            fl.append(final)

    dist=get_dist(st,fl)
    # new_dist=route_dist(st,fl)
    sorted_dist=dist[0]
    new_cord=dist[1]
    final_route=None

    end=list()
    route_no = ""

    for i in range(len(sorted_dist)):
        index=sorted_dist[i][0]
        new_lon= new_cord[index][0]
        new_lat= new_cord[index][1]
        response=requests.get("https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"+str(start_lon)+","+str(start_lat)+";"+str(new_lon)+","+str(new_lat)+"?geometries=geojson&access_token=pk.eyJ1IjoiaGFsb2xpbWF0IiwiYSI6ImNqZWRrcjM2bTFrcWEzMmxucDQ4N2kxaDMifQ.Buarvvdqz7yJ1O25up2SzA")
        all_data=json.loads(response.content)
        # print i,all_data
        try:
            for r in range(len(all_data['routes'])):
                route = all_data['routes'][r]['geometry']
                all_cords = route['coordinates']

                res = flood_check(all_cords,s)
                if res == "flooded route":
                    continue
                if res == "route safe":
                    end.append(new_lon)
                    end.append(new_lat)
                    final_route=route
                    route_no=r
            if final_route is None:
                continue
            else:
                break
        except:
            end.append(start_lon)
            end.append(start_lat)
            route_no="not available"
            break
    new_name=""
    if route_no!="not available":
        for e in d["features"]:
            if e["geometry"]["coordinates"]==end:
                new_name=e["properties"]["name"]
                # print new_name
                break
    if new_name=="":
        j= json.dumps({"end":end,"route_no":route_no,"phone":"not available"});
    else:
        try:
            new_lon=end[0]
            new_lat=end[1]
            response1=requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(new_lat)+","+str(new_lon)+"&radius=500&keyword="+new_name+"&key=AIzaSyANUmhGp9RnNMVg4yZCIF-P0lMovGbTNEg")
            all_data1=json.loads(response1.content)
            place_id=all_data1["results"][0]["place_id"]
            response=requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid="+place_id+"&key=AIzaSyANUmhGp9RnNMVg4yZCIF-P0lMovGbTNEg")
            all_data=json.loads(response.content)
            phone_numb= all_data["result"]["formatted_phone_number"]
            address=all_data["result"]["formatted_address"]
            all_data=new_name+","+"contact information : "+address+" "+str(phone_numb)
        except:
            all_data="not available"
        j= json.dumps({"end":end,"route_no":route_no,"phone":all_data});


    # print j
    return j

def flood_check(cordin,strt):
    # print len(cordin)
    cordin = interpolate_try(cordin,strt)
    # print cordin
    # print len(cordin)
    f=None
    for e in cordin:
        # print e
        ln=e[0]
        lt = e[1]
        # print type(ln),lt
        f=None
        n_end=list()
        n_end.append(lt)
        n_end.append(ln)
        dis=great_circle(strt, n_end).kilometers
        geohash = Geohash.encode(ln,lt, precision=8)
        if geohash_dict.get(geohash) is not None:
            x=geohash_dict[geohash]
        else:
            x="No Satellite Data!"
        # print x
        if str(x)=="True" and dis>0.5:
            # print "entered true"
            f="flooded route"
            break
    # print f
    if f=="flooded route":
        return f
    else:
        return "route safe"

@application.route("/data", methods=['GET','POST'])
def get_data():
    dataset = request.form['dataset']
    read_data(dataset)
    map_ = index(dataset)
    return map_


def read_data(dataset):
# dataset="houston"
    # dataset=request.args.get('dataset')
    global sh,rs,inf,ph_sh,ph_rs,ph_inf,other_s,other_r,other_i,centroid

    if dataset=="houston":
        centroid=[-95.3635526899414,29.759425736966094]
    elif dataset=="chennai":
        centroid=[80.21378369330633,13.018400446841508]

    r = requests.get('http://localhost:9200')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    s=[]
    for i in range(9000):
        try:
            s.append(es.get(index=dataset+'-tweets', doc_type='people', id=i)["_source"])
        except:
            break
    # print s

    p=[]
    for c in range(9000):
        try:
            p.append(es.get(index=dataset+'1', doc_type='locs', id=c)["_source"])
        except:
            break

    crowd=[]
    for c in range(9000):
        try:
            crowd.append(es.get(index=dataset+'-crowd', doc_type='crowd', id=c)["_source"])
        except:
            break

    shelter=list()
    rescue=list()
    infra=list()
    for e in s:
        if e["properties"]["class"]=="shelter_matching":
            shelter.append(e)
        elif e["properties"]["class"]=="rescue_match":
            rescue.append(e)
        else:
            infra.append(e)
    sh=str(json.dumps({"type": "FeatureCollection", "features": shelter}))
    rs=str(json.dumps({"type": "FeatureCollection", "features": rescue}))
    inf=str(json.dumps({"type": "FeatureCollection", "features": infra}))
    ph_shelter=list()
    ph_rescue=list()
    ph_infra=list()
    for e in p:
        if e["properties"]["class"]=="shelter_matching":
            ph_shelter.append(e)
        elif e["properties"]["class"]=="rescue_match":
            ph_rescue.append(e)
        else:
            ph_infra.append(e)
    ph_sh=str(json.dumps({"type": "FeatureCollection", "features": ph_shelter}))
    ph_rs=str(json.dumps({"type": "FeatureCollection", "features": ph_rescue}))
    ph_inf=str(json.dumps({"type": "FeatureCollection", "features": ph_infra}))
    other_shelter=list()
    other_rescue=list()
    other_infra=list()
    for e in crowd:
        if e["properties"]["class"]=="shelter_matching":
            other_shelter.append(e)
        elif e["properties"]["class"]=="rescue_match":
            other_rescue.append(e)
        else:
            other_infra.append(e)
    other_s=str(json.dumps({"type": "FeatureCollection", "features": other_shelter}))
    other_r=str(json.dumps({"type": "FeatureCollection", "features": other_rescue}))
    other_i=str(json.dumps({"type": "FeatureCollection", "features": other_infra}))


@application.route("/<gaz_name>")
def index(gaz_name):
    if gaz_name not in ["chennai","houston"]:
        options = """
            <p> </p>
        """
        return options
    
    gaz_name=gaz_name.lower()
    # print "came to index"

    read_data(gaz_name)

    map = make_map( centroid=centroid,
                    shelter_data=sh,
                    rescue_data=rs,
                    photon_shelter=ph_sh,
                    photon_rescue=ph_rs,
                    other_sh=other_s,
                    other_res=other_r)

    return map


@application.route('/test', methods=['GET','POST'])
def check_selected():
    with open("_Data/chennai.geojson") as f:
        data = json.load(f)
    data["features"] = data["features"][0::3]
    return json.dumps(data)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8088)
    # interpolate_try()
    # intp() 
