"""
This module contains SVG logo and icon data for the Planetary Health Dashboard
"""

# Earth logo SVG
earth_logo_svg = """
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Ocean/Water Base -->
  <circle cx="50" cy="50" r="45" fill="#2980b9"/>
  
  <!-- Land Masses -->
  <path d="M40,15 Q60,20 75,30 Q85,40 90,60 Q80,70 70,75 Q50,85 25,70 Q15,50 20,30 Q30,20 40,15" fill="#27ae60"/>
  <path d="M40,90 Q50,85 60,90 Q70,85 70,80 Q60,75 45,80 Q35,85 40,90" fill="#27ae60"/>
  
  <!-- Ice Caps -->
  <path d="M45,10 Q55,8 65,15 Q55,12 45,10" fill="#ecf0f1"/>
  <path d="M35,90 Q45,95 55,92 Q45,90 35,90" fill="#ecf0f1"/>
  
  <!-- Subtle Cloud Patterns -->
  <path d="M20,30 Q25,25 30,30 Q35,28 30,35 Q25,38 20,30" fill="#ecf0f1" fill-opacity="0.7"/>
  <path d="M65,20 Q70,15 75,20 Q80,18 75,25 Q70,28 65,20" fill="#ecf0f1" fill-opacity="0.7"/>
  
  <!-- Global Grid Lines -->
  <circle cx="50" cy="50" r="45" stroke="#3498db" stroke-width="0.5" fill="none"/>
  <ellipse cx="50" cy="50" rx="45" ry="15" stroke="#3498db" stroke-width="0.5" fill="none"/>
  <ellipse cx="50" cy="50" rx="30" ry="10" stroke="#3498db" stroke-width="0.5" fill="none"/>
  <line x1="5" y1="50" x2="95" y2="50" stroke="#3498db" stroke-width="0.5"/>
  <line x1="50" y1="5" x2="50" y2="95" stroke="#3498db" stroke-width="0.5"/>
</svg>
"""

# Header styling with Earth icon and title
header_html = """
<div style="display: flex; align-items: center; margin-bottom: 20px; background-color: #f5f7f9; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <div style="margin-right: 20px;">
        {earth_logo_svg}
    </div>
    <div>
        <h1 style="color: #1AB394; margin: 0; padding: 0; font-size: 2.5rem;">Planetary Health Dashboard</h1>
        <p style="color: #7f8c8d; margin: 5px 0 0 0; padding: 0; font-size: 1.1rem;">
            Real-time monitoring of Earth's vital signs
        </p>
    </div>
</div>
"""

# Card container for metrics and visualizations
card_html = """
<div style="background-color: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <h3 style="color: #2c3e50; margin-top: 0; margin-bottom: 15px; border-bottom: 1px solid #f0f2f6; padding-bottom: 10px;">
        {title}
    </h3>
    {content}
</div>
"""

# Footer with attribution and info
footer_html = """
<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #f0f2f6; text-align: center; font-size: 0.8rem; color: #7f8c8d;">
    <p>
        Planetary Health Dashboard | Data Last Updated: {date} | Built with 
        <span style="color: #e74c3c; font-size: 1rem;">♥</span> for Earth
    </p>
</div>
"""