def filter_girr_products(trades):
    """
    GIRR hesaplaması için uygun olan ürünleri filtreler.
    
    Args:
        trades (list):
        
    Returns:
        list: Sadece GIRR hesaplamasına uygun ürünlerin bulunduğu liste.
    """
    girr_types = {"fixed_rate_bond", "floating_rate_bond", "interest_rates_swap"}
    return [trade for trade in trades if trade.get("calculation_type") in girr_types]
