from pydantic import BaseModel



class KPIs(BaseModel):
    '''Modelo para os dados do dashboard.'''
    total_revenue: float
    total_sales: int
    total_bookings: int
    total_customers: int