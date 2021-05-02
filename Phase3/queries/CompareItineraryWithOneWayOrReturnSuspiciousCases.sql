select
    *
from
    (
    select
        distinct transactiondateutc,
        uniqueid,
        itinerary,
        arryofitinerary[safe_offset(0)] first_element,
        array_reverse(arryofitinerary)[safe_offset(0)] last_element,
        onewayorreturn
    from
        (
        select
            transactiondateutc,
            uniqueid,
            split(itinerary,
            "-") arryofitinerary,
            itinerary,
            onewayorreturn
        from
            `assessmentdb.transactions` ) )
where
    ( (onewayorreturn = 'One Way'
    and first_element = last_element)
    or (onewayorreturn = 'Return'
    and first_element <> last_element) )