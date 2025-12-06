// Zalf Innfiltration


    
const lakesFeatureGroup = new L.FeatureGroup()
lakesFeatureGroup.toolTag = 'infiltration';
const streamsFeatureGroup = new L.FeatureGroup()
streamsFeatureGroup.toolTag = 'infiltration';
const inletConnectionsFeatureGroup = new L.FeatureGroup()
inletConnectionsFeatureGroup.toolTag = 'infiltration';
let sinkCluster = L.markerClusterGroup();
sinkCluster.toolTag = 'infiltration';
let enlargedSinkCluster = L.markerClusterGroup();
enlargedSinkCluster.toolTag = 'infiltration';

// TUB Injection
const tubInjectionTileLayer = new L.TileLayer();
tubInjectionTileLayer.toolTag = 'injection';

// SiekerWetlands
const siekerWetlandFeatureGroup = new L.FeatureGroup();
siekerWetlandFeatureGroup.toolTag = 'wetland';
const siekerWetlandLakeFeatureGroup = new L.FeatureGroup();
siekerWetlandLakeFeatureGroup.toolTag = 'wetland';
const siekerWetlandStreamFeatureGroup = new L.FeatureGroup();
siekerWetlandStreamFeatureGroup.toolTag = 'wetland';
const siekerWetlandResultFeatureGroup = new L.FeatureGroup();
siekerWetlandResultFeatureGroup.toolTag = 'wetland';

//SiekerSink
const siekerSinkFeatureGroup = new L.markerClusterGroup();
siekerSinkFeatureGroup.toolTag = 'sieker_sink';
const siekerLakeFeatureGroup = new L.FeatureGroup();
siekerLakeFeatureGroup.toolTag = 'sieker_sink';
const siekerStreamFeatureGroup = new L.FeatureGroup();
siekerStreamFeatureGroup.toolTag = 'sieker_sink';
const siekerSinkResultFeatureGroup = new L.FeatureGroup();
siekerSinkResultFeatureGroup.toolTag = 'sieker_sink';

// SierkerSurfaceWaters
const siekerLakesFeatureGroup = new L.FeatureGroup();
siekerLakesFeatureGroup.toolTag = 'sieker_surface_water'
const waterLevelsFeatureGroup = new L.FeatureGroup();
waterLevelsFeatureGroup.toolTag = 'sieker_surface_water';
const filteredLakesFeatureGroup = new L.FeatureGroup();
filteredLakesFeatureGroup.toolTag = 'sieker_surface_water';
const abovegroundCatchmentFeatureGroup = new L.FeatureGroup();
abovegroundCatchmentFeatureGroup.toolTag = 'sieker_surface_water';


//siekerGek
const siekerGekFeatureGroup = new L.FeatureGroup()
siekerGekFeatureGroup.toolTag = 'sieker_gek';
const filteredSiekerGekFeatureGroup = new L.FeatureGroup();
filteredSiekerGekFeatureGroup.toolTag = 'sieker_gek'


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
    'sink_embankment': inletConnectionsFeatureGroup,
    // SiekerWetland
    'wetland': siekerWetlandFeatureGroup,
    'wetland_lake': siekerWetlandLakeFeatureGroup,
    'wetland_stream': siekerWetlandStreamFeatureGroup,
    'wetland_result': siekerWetlandResultFeatureGroup,
    'wetland_result_inlet': siekerWetlandResultFeatureGroup,
    'wetland_result_wetland': siekerWetlandResultFeatureGroup,

    // SiekerSurfaceWaters
    'sieker_surface_water': siekerLakesFeatureGroup,
    'sieker_water_level': waterLevelsFeatureGroup,
    'filtered_sieker_surface_water': filteredLakesFeatureGroup,
    'above_ground_catchment_area': abovegroundCatchmentFeatureGroup,
    // SiekerSink
    'sieker_sink': siekerSinkFeatureGroup, 
    'sieker_lake' : siekerLakeFeatureGroup,
    'sieker_stream': siekerStreamFeatureGroup,
    'sieker_sink_result': siekerSinkResultFeatureGroup,
    'sieker_sink_result_inlet': siekerSinkResultFeatureGroup,
    'sieker_sink_result_sink': siekerSinkResultFeatureGroup,
    // SiekerGek
    'sieker_gek': siekerGekFeatureGroup,
    'filtered_sieker_gek': filteredSiekerGekFeatureGroup,
  
    
    'drainage_probability': siekerDrainageRasterTile,
    // drained Areas
    'pumping_station': drainedAreaPumpingStations,
    'drainage': drainedAreaDrainages,
    'drained_area': [ drainedAreaPumpingStations, drainedAreaDrainages ],
    // drainage network
    'drainage_network': [
        naturalCreekUnshadedFeatureGroup,
        naturalCreekShadedFeatureGroup,
        ditchFeatureGroup,
        canalShadedFeatureGroup,
        canalUnshadedFeatureGroup,
        nonNaturalCreekShadedFeatureGroup,
        nonNaturalCreekPartlyShadedFeatureGroup,
        nonNaturalCreekUnshadedFeatureGroup,
        drainagePipeFeatureGroup,
        suckerFeatureGroup,
        collectorFeatureGroup,
        naturalRiverFeatureGroup
    ],

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


