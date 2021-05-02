select
    distinct transactiondateutc,
    uniqueid,
    itinerary
from
    (
    select
        transactiondateutc,
        uniqueid,
        itinerary,
        lag(segment_arrivalairportcode,1) 
            over(partition by uniqueid
                order by segment_segmentnumber,
                         segment_legnumber
                ) before_segment_arrivalairportcode,
        segment_departureairportcode,
        segment_arrivalairportcode
    from
        `assessmentdb.transactions`)
where
    segment_departureairportcode <> before_segment_arrivalairportcode
