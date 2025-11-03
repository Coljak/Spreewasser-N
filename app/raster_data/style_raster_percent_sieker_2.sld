<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>Entwaesserungswahrscheinlichkeit_9Parameter_v2</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="ramp">
              <sld:ColorMapEntry color="#d7191c" quantity="14.285714149475098" label="14.2857"/>
              <sld:ColorMapEntry color="#fdae61" quantity="35.714285612106323" label="35.7143"/>
              <sld:ColorMapEntry color="#ffffc0" quantity="57.142857074737549" label="57.1429"/>
              <sld:ColorMapEntry color="#a6d96a" quantity="78.571428537368774" label="78.5714"/>
              <sld:ColorMapEntry color="#1a9641" quantity="100" label="100.0000"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
