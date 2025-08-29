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


export const Layers = {
    // Infiltration
    'sink':  sinkCluster,
    // 'sink-clustered': sinkCluster,
    'enlarged_sink': enlargedSinkCluster,
    // 'enlarged_sink-clustered': enlargedSinkCluster,
    'lake': lakesFeatureGroup,
    'stream': streamsFeatureGroup,
    'inletConnectionsFeatureGroup': inletConnectionsFeatureGroup,


}

