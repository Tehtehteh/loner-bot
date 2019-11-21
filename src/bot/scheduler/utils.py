from typing import Union


def make_ticket_order_job_id(username: str,
                             departure_station_id: Union[str, int],
                             arrival_station_id: Union[str, int],
                             date: str) -> str:
    job_id = f'ticket-booking-{username}-{departure_station_id}-{arrival_station_id}-{date}'
    return job_id
