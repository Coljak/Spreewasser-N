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

const siekerWetlandFeatureGroup = new L.FeatureGroup()
siekerWetlandFeatureGroup.toolTag = 'sieker_wetland';

const siekerFilteredWetlandFeatureGroup = new L.FeatureGroup()
siekerFilteredWetlandFeatureGroup.toolTag = 'sieker_wetland';

const siekerSinkFeatureGroup = new L.markerClusterGroup();
siekerSinkFeatureGroup.toolTag = 'sieker_sink';


// SierkerSurfaceWaters
const siekerLakesFeatureGroup = new L.FeatureGroup();
siekerLakesFeatureGroup.toolTag = 'sieker-surface-waters'
const waterLevelsFeatureGroup = new L.FeatureGroup();
waterLevelsFeatureGroup.toolTag = 'sieker-surface-waters';
const filteredLakesFeatureGroup = new L.FeatureGroup();
filteredLakesFeatureGroup.toolTag = 'sieker-surface-waters';

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
    'sieker_large_lake': lakesFeatureGroup,
    'sieker_water_level': waterLevelsFeatureGroup,
    'filtered_sieker_large_lake': filteredLakesFeatureGroup,
    // SiekerSink
    'sieker_sink': siekerSinkFeatureGroup,
    
    // SiekerGek
    // TUInjection


}

