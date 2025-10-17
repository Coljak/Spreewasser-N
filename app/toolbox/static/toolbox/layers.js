const sinkFeatureGroup = new L.FeatureGroup()
sinkFeatureGroup.toolTag = 'infiltration';
const sinkPointFeatureGroup = new L.FeatureGroup()
sinkPointFeatureGroup.toolTag = 'infiltration';
const enlargedSinkFeatureGroup = new L.FeatureGroup()
enlargedSinkFeatureGroup.toolTag = 'infiltration';
const lakesFeatureGroup = new L.FeatureGroup()
lakesFeatureGroup.toolTag = 'infiltration';
const streamsFeatureGroup = new L.FeatureGroup()
streamsFeatureGroup.toolTag = 'infiltration';
const inletConnectionsFeatureGroup = new L.featureGroup()
inletConnectionsFeatureGroup.toolTag = 'infiltration';
let sinkCluster = L.markerClusterGroup();
sinkCluster.toolTag = 'infiltration';
let enlargedSinkCluster = L.markerClusterGroup();
enlargedSinkCluster.toolTag = 'infiltration';

// SiekerWetlands
const siekerWetlandFeatureGroup = new L.FeatureGroup()
siekerWetlandFeatureGroup.toolTag = 'sieker_wetland';
const siekerFilteredWetlandFeatureGroup = new L.FeatureGroup()
siekerFilteredWetlandFeatureGroup.toolTag = 'sieker_wetland';

const siekerSinkFeatureGroup = new L.markerClusterGroup();
siekerSinkFeatureGroup.toolTag = 'sieker_sink';


// SierkerSurfaceWaters
const siekerLakesFeatureGroup = new L.FeatureGroup();
siekerLakesFeatureGroup.toolTag = 'sieker_surface_water'
const waterLevelsFeatureGroup = new L.FeatureGroup();
waterLevelsFeatureGroup.toolTag = 'sieker_surface_water';
const filteredLakesFeatureGroup = new L.FeatureGroup();
filteredLakesFeatureGroup.toolTag = 'sieker_surface_water';

//siekerGek
const siekerGekFeatureGroup = new L.FeatureGroup()
siekerGekFeatureGroup.toolTag = 'sieker-gek';

const siekerFilteredGekFeatureGroup = new L.FeatureGroup()
siekerFilteredGekFeatureGroup.toolTag = 'sieker-gek';

export const Layers = {
    // Infiltration
    'sink':  sinkCluster,
    'enlarged_sink': enlargedSinkCluster,
    'lake': lakesFeatureGroup,
    'stream': streamsFeatureGroup,
    'inletConnectionsFeatureGroup': inletConnectionsFeatureGroup,
    // SiekerWetland
    'sieker_wetland': siekerWetlandFeatureGroup,
    'filtered_sieker_wetland': siekerFilteredWetlandFeatureGroup,
    // SiekerSurfaceWaters
    'sieker_surface_water': siekerLakesFeatureGroup,
    'sieker_water_level': waterLevelsFeatureGroup,
    'filtered_sieker_surface_water': filteredLakesFeatureGroup,
    // SiekerSink
    'sieker_sink': siekerSinkFeatureGroup,   
    // SiekerGek
    'sieker_gek': siekerGekFeatureGroup,
    'filtered_sieker_gek': siekerFilteredGekFeatureGroup,
    // TUInjection


}

