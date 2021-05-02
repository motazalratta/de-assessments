select  transactiondateutc,
        uniqueid,
        itinerary,
        segment_itinerary
from (
    select
        transactiondateutc,
        uniqueid,
        itinerary,
        concat(segment_itinerary_first_element, '-', segment_itinerary_without_first_element) segment_itinerary
    from
        (
        select
            distinct 
            transactiondateutc,
            uniqueid,
            itinerary,
            string_agg(segment_arrivalairportcode,"-") 
                over (partition by uniqueid,transactiondateutc
                        order by
                                segment_segmentnumber,
                                Segment_legnumber 
                        rows between unbounded preceding and unbounded following
                        ) as segment_itinerary_without_first_element,
            first_value(segment_departureairportcode) 
                 over (partition by uniqueid,transactiondateutc
                        order by
                                segment_segmentnumber,
                                segment_legnumber
                       ) as segment_itinerary_first_element
        from `assessmentdb.transactions` 
        )
    )
    where segment_itinerary <> itinerary