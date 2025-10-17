<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>hydraulic_conductivity_classified_v1</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#440154" quantity="10" label="&lt; 5 K(m/d)"/>
              <sld:ColorMapEntry color="#3b528b" quantity="50" label="5 - 10 K(m/d)"/>
              <sld:ColorMapEntry color="#21908d" quantity="100" label="10 -20 K(m/d)"/>
              <sld:ColorMapEntry color="#5dc963" quantity="200" label="20 - 30 K(m/d)"/>
              <sld:ColorMapEntry color="#fde725" quantity="300" label="> 30 K(m/d)"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
