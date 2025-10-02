<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>distance_to_extraction_wells_v1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#d7191c" quantity="10" label="Zone 1 und 2"/>
              <sld:ColorMapEntry color="#1a9641" quantity="20" label="Zone 3 oder 30 Jahre Isochron"/>
              <sld:ColorMapEntry color="#a6d96a" quantity="30" label="Im Einzugsgebiet"/>
              <sld:ColorMapEntry color="#ffffc0" quantity="40" label="Auserhalb d. Einzugsgebiets, &lt; 5km"/>
              <sld:ColorMapEntry color="#fdae61" quantity="50" label="Auserhalb d. Einzugsgebiets, > 5km"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
