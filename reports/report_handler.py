import pandas as pd
from db_handler import DatabaseManager

class ReportHandler(DatabaseManager):
    """Handles report-related database queries."""

    def get_supplier_performance_data(self):
        """Fetch purchase order data for supplier performance analysis."""
        query = """
        SELECT 
            po.POID, po.ExpectedDelivery, po.ActualDelivery, 
            po.Status, s.SupplierName,
            poi.OrderedQuantity, poi.ReceivedQuantity
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        WHERE po.Status = 'Completed'
        """
        return self.fetch_data(query)
