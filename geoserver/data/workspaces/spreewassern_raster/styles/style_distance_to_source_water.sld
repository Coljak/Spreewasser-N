<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>distance_to_source_water_v1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#d7191c" quantity="10" label="&lt; 250m"/>
              <sld:ColorMapEntry color="#f59053" quantity="20" label="250 -500m"/>
              <sld:ColorMapEntry color="#1a9641" quantity="30" label="500 - 800m"/>
              <sld:ColorMapEntry color="#8acc62" quantity="40" label="800 - 1200m"/>
              <sld:ColorMapEntry color="#dbf09e" quantity="50" label="1200 - 1500m"/>
              <sld:ColorMapEntry color="#fedf9a" quantity="60" label="> 1500m"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>