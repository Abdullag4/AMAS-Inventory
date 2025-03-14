import streamlit as st
from db_handler import DatabaseManager

class ReportHandler(DatabaseManager):
    """Handles fetching report data from the database."""

    def get_supplier_performance(self):
        """Fetch supplier performance data based on PO fulfillment."""
        query = """
        SELECT 
            s.SupplierID,
            s.SupplierName,
            COUNT(po.POID) AS TotalOrders,
            SUM(CASE WHEN po.ActualDelivery <= po.ExpectedDelivery THEN 1 ELSE 0 END) AS OnTimeDeliveries,
            SUM(CASE WHEN po.ActualDelivery > po.ExpectedDelivery THEN 1 ELSE 0 END) AS LateDeliveries,
            AVG(GREATEST(0, DATE_PART('day', po.ActualDelivery - po.ExpectedDelivery))) AS AvgLateDays,
            SUM(CASE WHEN poi.ReceivedQuantity = poi.OrderedQuantity THEN 1 ELSE 0 END) AS CorrectQuantityOrders,
            SUM(CASE WHEN poi.ReceivedQuantity <> poi.OrderedQuantity THEN 1 ELSE 0 END) AS QuantityMismatchOrders
        FROM PurchaseOrders po
        JOIN Supplier s ON po.SupplierID = s.SupplierID
        JOIN PurchaseOrderItems poi ON po.POID = poi.POID
        WHERE po.Status = 'Completed'
        GROUP BY s.SupplierID, s.SupplierName
        ORDER BY OnTimeDeliveries DESC;
        """
        return self.fetch_data(query)
