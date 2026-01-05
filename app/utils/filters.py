from flask import Flask


def register_filters(app: Flask):
    """Register custom Jinja2 filters"""

    @app.template_filter('price_display')
    def price_display(price_level):
        """Convert price level to dollar signs"""
        if price_level is None:
            return "N/A"
        if price_level == 0:
            return "Free"
        return "$" * price_level

    @app.template_filter('distance_display')
    def distance_display(distance_meters):
        """Convert meters to miles with 1 decimal place"""
        if distance_meters is None:
            return "N/A"
        miles = distance_meters * 0.000621371
        return f"{miles:.1f} mi"

    @app.template_filter('rating_stars')
    def rating_stars(rating):
        """Convert rating to star display"""
        if rating is None:
            return "Not rated"

        full_stars = int(rating)
        half_star = (rating - full_stars) >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)

        stars = "★" * full_stars
        if half_star:
            stars += "½"
        stars += "☆" * empty_stars

        return f"{stars} ({rating:.1f})"

    @app.template_filter('format_phone')
    def format_phone(phone):
        """Format phone number"""
        if not phone:
            return "N/A"
        return phone

    @app.template_filter('truncate_address')
    def truncate_address(address, max_length=50):
        """Truncate long addresses"""
        if not address:
            return "N/A"
        if len(address) <= max_length:
            return address
        return address[:max_length-3] + "..."
