select 
transactiondateutc,
tran.uniqueid,
tran.originairportcode,loc_orig.countryname originairportcode_countery,
tran.destinationairportcode, loc_dest.countryname destinationairportcode_countery,
tran.segment_arrivalairportcode,loc_seg_arr.countryname segment_arrivalairportcode_countery,
tran.segment_departureairportcode,loc_seg_dep.countryname segment_departureairportcode_countery
from           `assessmentdb.transactions` tran
    left join  `assessmentdb.locations` loc_orig
         on tran.originairportcode               = loc_orig.airportcode 
    left join  `assessmentdb.locations` loc_dest
         on tran.destinationairportcode          = loc_dest.airportcode 
    left join  `assessmentdb.locations` loc_seg_arr
        on tran.segment_arrivalairportcode       = loc_seg_arr.airportcode 
    left join  `assessmentdb.locations` loc_seg_dep
        on tran.segment_departureairportcode     = loc_seg_dep.airportcode 
where loc_orig.countryname is null
or loc_dest.countryname is null
or loc_seg_dep.countryname is null
or loc_seg_arr.countryname is null
or originairportcode is null
or destinationairportcode is null
or segment_arrivalairportcode is null
or segment_departureairportcode is null
or loc_seg_arr.countryname is null