
UPDATE swn_bueksoilprofile 
SET gen_id = t1.gen_id,
        bf_id = t1.bf_id
FROM bk_horizonte t1 
JOIN bk_profile t2 ON t1.gen_id = t2.gen_id AND t1.bf_id = t2.bf_id
JOIN swn_bueksoilprofile st2 ON t2.polygon_id = st2.polygon_id 
                                                            AND t2.flant_mittelw = st2.area_percenteage 
                                                            AND st2.system_unit = t2.bo_subtyp 
                                                            AND t2.bof_nr = st2.soil_profile_no 
JOIN swn_bueksoilprofilehorizon st1 ON st2.id = st1.bueksoilprofile_id 
                                                                        AND t1.otief = st1.obergrenze_m * 10 
                                                                        AND t1.utief = st1.untergrenze_m * 10
WHERE t2.polygon_id = st2.polygon_id 
    AND t2.flant_mittelw = st2.area_percenteage 
    AND st2.system_unit = t2.bo_subtyp 
    AND t2.bof_nr = st2.soil_profile_no 
    AND st2.id = st1.bueksoilprofile_id 
    AND t1.otief = st1.obergrenze_m * 10 
    AND t1.utief = st1.untergrenze_m * 10;
