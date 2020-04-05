import React from 'react';
import axios from 'axios';
import Grid from '@material-ui/core/Grid';
import { ToastsContainer, ToastsStore } from 'react-toasts';

// Start Openlayers imports
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import {fromLonLat} from 'ol/proj';
import Circle from 'ol/geom/Circle';
import CircleStyle from 'ol/style/Circle';
import Fill from 'ol/style/Fill';

import { 
    Map,
    View
 } from 'ol'
import {
    GeoJSON,
    XYZ
} from 'ol/format'
import {
    Tile as TileLayer,
    Vector as VectorLayer
} from 'ol/layer'
import {
    Vector as VectorSource,
    OSM as OSMSource,
    XYZ as XYZSource,
    TileWMS as TileWMSSource
} from 'ol/source'
import {
    Select as SelectInteraction,
    defaults as DefaultInteractions
} from 'ol/interaction'
import { 
    Attribution,
    ScaleLine,
    ZoomSlider,
    Zoom,
    Rotate,
    MousePosition,
    OverviewMap,
    defaults as DefaultControls
} from 'ol/control'
import {
    Style,
    Fill as FillStyle,
    RegularShape as RegularShapeStyle,
    Stroke as StrokeStyle
} from 'ol/style'

import { 
    Projection,
    get as getProjection
 } from 'ol/proj'

// End Openlayers imports

class MapComponent extends React.Component {
    constructor(props) {
        super(props)
        this.updateDimensions = this.updateDimensions.bind(this)
    }
    updateDimensions(){
        //const h = window.innerWidth >= 992 ? window.innerHeight : 400
		const h = 650
        this.setState({height: h})
    }
    componentWillMount(){
        window.addEventListener('resize', this.updateDimensions)
        this.updateDimensions()
    }
    componentDidMount(){
		
		// Create an Openlayer Map instance with two tile layers
        const map = new Map({
            //  Display the map in the div with the id of map
            target: 'map',
            layers: [
                new TileLayer({
                    source: new XYZSource({
                        url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        projection: 'EPSG:3857'
                    })
                }),
                new TileLayer({
                    source: new TileWMSSource({
                        url: 'https://ahocevar.com/geoserver/wms',
                        params: {
                            layers: 'topp:states',
                            'TILED': true,
                        },
                        projection: 'EPSG:4326'
                    }),
                    name: 'USA'
                }),
            ],
            // Add in the following map controls
            controls: DefaultControls().extend([
                new ZoomSlider(),
                new MousePosition(),
                new ScaleLine(),
                new OverviewMap()
            ]),
            // Render the tile layers in a map view with a Mercator projection
            view: new View({
                projection: 'EPSG:3857',
                center: [8639889.395961922, 1457435.993909429],
                zoom: 12.5
            })
        })
		
		var centroid_array = [];
		
		axios.get("http://127.0.0.1:8000/api/tree/clusters").then((res)=>{
			var clusters_list = res.data.clusters;
			//alert(clusters_list);
			console.log(clusters_list);
			for (var i = 0; i < clusters_list.length; i++)
			{
				//alert(clusters_list[i].centroid);
				
				var marker = new Feature({
				  geometry: new Circle(clusters_list[i].centroid, 2000)
				});
				
				var vectorSource = new VectorSource({
				  features: [marker]
				});
				var markerVectorLayer = new VectorLayer({
				  source: vectorSource,
				});
				
				map.addLayer(markerVectorLayer);
				//alert("Ha");
			}
		});
    }
    componentWillUnmount(){
        window.removeEventListener('resize', this.updateDimensions)
    }
    render(){
        const style = {
            width: '70%',
            height:this.state.height,
            backgroundColor: '#cccccc',
        }
        return (
            <Grid container>
                <Grid item xs={12}>
                    <div id='map' style={style} >
                    </div>
                </Grid>
            </Grid>
        )
    }
}
export default MapComponent;