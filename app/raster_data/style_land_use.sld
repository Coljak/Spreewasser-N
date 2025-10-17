<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>land_use</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap type="values">
              <sld:ColorMapEntry color="#ee7546" quantity="20" label="Shrubs"/>
              <sld:ColorMapEntry color="#e34731" quantity="30" label="Grünland/Büsche"/>
              <sld:ColorMapEntry color="#faa35c" quantity="40" label="Ackerland"/>
              <sld:ColorMapEntry color="#d7191c" quantity="50" label="Urban"/>
              <sld:ColorMapEntry color="#2b83ba" quantity="80" label="Wasser"/>
              <sld:ColorMapEntry color="#529fb3" quantity="90" label="Feuchtgebiete"/>
              <sld:ColorMapEntry color="#fdc177" quantity="111" label="Geschlossener Nadelwald"/>
              <sld:ColorMapEntry color="#feda94" quantity="114" label="Geschlossener Laubwald"/>
              <sld:ColorMapEntry color="#fff3b1" quantity="115" label="Geschlossener Mischwald"/>
              <sld:ColorMapEntry color="#f2fabb" quantity="116" label="Geschlossener Wald"/>
              <sld:ColorMapEntry color="#d8efb3" quantity="121" label="Offener Nadelwald"/>
              <sld:ColorMapEntry color="#bee5aa" quantity="124" label="Offener Laubwald"/>
              <sld:ColorMapEntry color="#a1d6a6" quantity="125" label="Offener Mischwald"/>
              <sld:ColorMapEntry color="#7abaac" quantity="126" label="Offener Wald"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
