-- soil_profile_all source

CREATE VIEW [soil_profile_all]
AS
SELECT 
       [z].[tkle_nr] AS [polygon_id], 
       [p].[bof_nr] AS [profile_id_in_polygon], 
       [p].[flant_spanne] AS [range_percentage_of_area], 
       [p].[flant_mittelw] AS [avg_range_percentage_of_area], 
       [h].[hor_nr] AS [horizon_id], 
       [h].[utief] / 10.0 AS [layer_depth], 
       [bdc].[raw_density_g_per_cm3] * 1000.0 AS [bulk_density], 
       ([bdc].[raw_density_g_per_cm3] - (0.9 * [clay])) * 1000.0 AS [raw_density], 
       [c].[corg] AS [soil_organic_carbon], 
       NULL AS [soil_organic_matter], 
       (IFNULL ([ph].[ph_value_from], [ph].[ph_value_to]) + IFNULL ([ph].[ph_value_to], [ph].[ph_value_from])) / 2.0 AS [ph], 
       [h].[boart] AS [KA5_texture_class], 
       [sc].[sand] * 100 AS [sand], 
       [sc].[clay] * 100 AS [clay], 
       ROUND (1 - [sand] - [clay], 2) * 100 AS [silt], 
       NULL AS [permanent_wilting_point], 
       NULL AS [field_capacity], 
       NULL AS [saturation], 
       NULL AS [soil_water_conductivity_coefficient], 
       NULL AS [sceleton], 
       NULL AS [soil_ammonium], 
       NULL AS [soil_nitrate], 
       NULL AS [c_n], 
       NULL AS [initial_soil_moisture], 
    [h].[horiz] AS [layer_description], 
    CASE 
        WHEN INSTR(LOWER([h].[horiz]), 'gr') > 0 AND INSTR(LOWER([h].[horiz]), 'gro') = 0 THEN 1 
        ELSE 0 
    END AS [is_in_groundwater], 
    0 AS [is_impenetrable]
FROM   [tblZuordnungGLE_BLE] AS [z]
       LEFT JOIN [tblProfile] AS [p] ON [z].[gen_id] = [p].[gen_id]
       LEFT JOIN [tblHorizonte] AS [h] ON [p].[gen_id] = [h].[gen_id] AND [p].[bf_id] = [h].[bf_id]
       LEFT JOIN [humus_class_to_corg] AS [c] ON SUBSTR ([h].[humus], 2, 1) = [c].[humus_class]
       LEFT JOIN [ka5_soiltype_to_sand_and_clay] AS [sc] ON [sc].[ka5_soiltype] = [h].[boart]
       LEFT JOIN [bulk_density_class_to_raw_density] AS [bdc] ON [bdc].[bulk_density_class] = SUBSTR ([h].[ld], 3, 1)
       LEFT JOIN [ph_class_to_ph_value] AS [ph] ON [ph].[ph_class] = [h].[ph]
WHERE  [h].[gen_id] NOT NULL
         AND [h].[ld] NOT NULL
         AND [sand] NOT NULL
ORDER  BY
          [polygon_id],
          [profile_id_in_polygon],
          [horizon_id];