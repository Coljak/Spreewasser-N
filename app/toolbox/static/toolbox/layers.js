// Zalf Innfiltration
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

// TUB Injection
const tubInjectionTileLayer = new L.TileLayer();
tubInjectionTileLayer.toolTag = 'injection';

// SiekerWetlands
const siekerWetlandFeatureGroup = new L.FeatureGroup()
siekerWetlandFeatureGroup.toolTag = 'sieker_wetland';
const siekerFilteredWetlandFeatureGroup = new L.FeatureGroup()
siekerFilteredWetlandFeatureGroup.toolTag = 'sieker_wetland';

//SiekerSink
const siekerSinkFeatureGroup = new L.markerClusterGroup();
siekerSinkFeatureGroup.toolTag = 'sieker_sink';
const siekerLakeFeatureGroup = new L.markerClusterGroup();
siekerLakeFeatureGroup.toolTag = 'sieker_sink';
const siekerStreamFeatureGroup = new L.markerClusterGroup();
siekerStreamFeatureGroup.toolTag = 'sieker_sink';

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

// SiekerDrainage
// probabilty
const siekerDrainageRasterTile = new L.TileLayer();
siekerDrainageRasterTile.toolTag = 'drainage';
// drained area
const drainedAreaPumpingStations = new L.FeatureGroup();
drainedAreaPumpingStations.toolTag = 'drainage';
const drainedAreaDrainages = new L.FeatureGroup();
drainedAreaDrainages.toolTag = 'drainage';
// drainage network
const naturalCreekUnshadedFeatureGroup = new L.FeatureGroup();
naturalCreekUnshadedFeatureGroup.toolTag = 'drainage';
const naturalCreekShadedFeatureGroup = new L.FeatureGroup();
naturalCreekShadedFeatureGroup.toolTag = 'drainage';
const ditchFeatureGroup = new L.FeatureGroup();
ditchFeatureGroup.toolTag = 'drainage';
const canalUnshadedFeatureGroup = new L.FeatureGroup();
canalUnshadedFeatureGroup.toolTag = 'drainage';
const canalShadedFeatureGroup = new L.FeatureGroup();
canalShadedFeatureGroup.toolTag = 'drainage';
const nonNaturalCreekShadedFeatureGroup = new L.FeatureGroup();
nonNaturalCreekShadedFeatureGroup.toolTag = 'drainage';
const nonNaturalCreekPartlyShadedFeatureGroup = new L.FeatureGroup();
nonNaturalCreekPartlyShadedFeatureGroup.toolTag = 'drainage';
const nonNaturalCreekUnshadedFeatureGroup = new L.FeatureGroup();
nonNaturalCreekUnshadedFeatureGroup.toolTag = 'drainage';
const collectorFeatureGroup = new L.FeatureGroup();
collectorFeatureGroup.toolTag = 'drainage';
const drainagePipeFeatureGroup = new L.FeatureGroup();
drainagePipeFeatureGroup.toolTag = 'drainage';
const suckerFeatureGroup = new L.FeatureGroup();
suckerFeatureGroup.toolTag = 'drainage';
const naturalRiverFeatureGroup = new L.FeatureGroup();
naturalRiverFeatureGroup.toolTag = 'drainage';

// natural_creeks #1
const naturalCreeksFeatureGroup = new L.FeatureGroup(
    [   naturalCreekUnshadedFeatureGroup,
        naturalCreekShadedFeatureGroup
    ]
);
naturalCreeksFeatureGroup.toolTag = 'drainage';

// ditches #2
const ditchesFeatureGroup = new L.FeatureGroup(
    [
        ditchFeatureGroup,
        canalShadedFeatureGroup,
        canalUnshadedFeatureGroup
    ]
);
ditchesFeatureGroup.toolTag = 'drainage';

// non_natural_creeks #3
const nonNaturalCreeksFeatureGroup = new L.FeatureGroup([
    nonNaturalCreekShadedFeatureGroup,
    nonNaturalCreekPartlyShadedFeatureGroup,
    nonNaturalCreekUnshadedFeatureGroup
]);
nonNaturalCreeksFeatureGroup.toolTag = 'drainage';

// pipes #4
const pipesFeatureGroup = new L.FeatureGroup([
    drainagePipeFeatureGroup,
    suckerFeatureGroup,
    collectorFeatureGroup
]);
pipesFeatureGroup.toolTag = 'drainage';

// rivers #5
const riversFeatureGroup = new L.FeatureGroup([
    naturalRiverFeatureGroup
]);
riversFeatureGroup.toolTag = 'drainage';



export const Layers = {
    // Infiltration
    'sink':  sinkCluster,
    'enlarged_sink': enlargedSinkCluster,
    'lake': lakesFeatureGroup,
    'stream': streamsFeatureGroup,
    'infiltration_result': inletConnectionsFeatureGroup,
    'infiltration_result_inlet': inletConnectionsFeatureGroup,
    'infiltration_result_sink': inletConnectionsFeatureGroup,
    'infiltration_result_enlarged_sink': inletConnectionsFeatureGroup,
    // SiekerWetland
    'sieker_wetland': siekerWetlandFeatureGroup,
    'filtered_sieker_wetland': siekerFilteredWetlandFeatureGroup,
    // SiekerSurfaceWaters
    'sieker_surface_water': siekerLakesFeatureGroup,
    'sieker_water_level': waterLevelsFeatureGroup,
    'filtered_sieker_surface_water': filteredLakesFeatureGroup,
    // SiekerSink
    'sieker_sink': siekerSinkFeatureGroup, 
    'sieker_lake' : siekerLakeFeatureGroup,
    'sieker_stream': siekerStreamFeatureGroup,
    // SiekerGek
    'sieker_gek': siekerGekFeatureGroup,
    'filtered_sieker_gek': siekerFilteredGekFeatureGroup,
    
    'drainage_probability': siekerDrainageRasterTile,
    // drained Areas
    'pumping_station': drainedAreaPumpingStations,
    'drainage': drainedAreaDrainages,
    // 'parents'
    // 'natural_creeks': naturalCreeksFeatureGroup,
    // 'ditches':  ditchesFeatureGroup,
    // 'non_natural_creeks':  nonNaturalCreeksFeatureGroup,
    // 'pipes': pipesFeatureGroup,
    // 'rivers': riversFeatureGroup,

    // 'parents'
    'natural_creeks': [   naturalCreekUnshadedFeatureGroup,
        naturalCreekShadedFeatureGroup
    ],
    'ditches':  [
        ditchFeatureGroup,
        canalShadedFeatureGroup,
        canalUnshadedFeatureGroup
    ],
    'non_natural_creeks':  [
        nonNaturalCreekShadedFeatureGroup,
        nonNaturalCreekPartlyShadedFeatureGroup,
        nonNaturalCreekUnshadedFeatureGroup
    ],
    'pipes': [
            drainagePipeFeatureGroup,
            suckerFeatureGroup,
            collectorFeatureGroup
        ],
    'rivers': [
            naturalRiverFeatureGroup
        ],

    'sucker': suckerFeatureGroup, // id=1
    'non_natural_creek_unshaded': nonNaturalCreekUnshadedFeatureGroup, // id=2
    'canal_shaded': canalShadedFeatureGroup, // id = 3
    'canal_unshaded': canalUnshadedFeatureGroup, // id = 4
    'non_natural_creek_partly_shaded': nonNaturalCreekPartlyShadedFeatureGroup,//id=5
    'drainage_pipe': drainagePipeFeatureGroup, // id=6
    'non_natural_creek_shaded': nonNaturalCreekShadedFeatureGroup, //7
    'natural_creek_shaded': naturalCreekShadedFeatureGroup, // 8
    'natural_river': naturalRiverFeatureGroup, // 9
    'collector': collectorFeatureGroup, // 10
    'ditch': ditchFeatureGroup, // 11
    'natural_creek_unshaded': naturalCreekUnshadedFeatureGroup, // 12


    // TUInjection
    'injection': tubInjectionTileLayer,
}


