from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
import re

class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance security by checking for common attack patterns
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for common SQL injection and XSS attacks
        self.sql_patterns = re.compile(
            r'(\s*([\0\b\'\"\n\r\t\%\_\\]*\s*(((select\s*.+\s*from)|(insert\s*.+\s*into)|(update\s*.+\s*set)|(delete\s*.+\s*from)|(drop\s*.+)|(truncate\s*.+)|(alter\s*.+)|(exec\s*.+)|(\s*(all|any|not|and|between|in|like|or|some|contains|containsall|containskey)\s*.+[\=\>\<=\!\~]+)|(let\s+.+[\=]\s*.+)|(begin\s*.*\s*end)|(if\s*.+\s*then\s*.+\s*else)|(union\s*.*\s*select))[\s\"\']*))|\-\-|\#)',
            re.IGNORECASE
        )
        self.xss_patterns = re.compile(
            r'<(script|iframe|embed|object|img|style|applet|body|html|head|link|meta|base|form|input|button|textarea|select|option|frameset|frame|video|audio|source|track|canvas|svg|math|noscript|template|shadow|element|slot|content|picture|source|time|data|menuitem|keygen|command|output|progress|meter|fieldset|legend|datalist|details|summary|dialog|menu|menuitem|dir|font|header|footer|main|section|article|aside|nav|address|blockquote|dd|div|dl|dt|figcaption|figure|hr|li|ol|p|pre|ul|a|abbr|b|bdi|bdo|br|cite|code|data|dfn|em|i|kbd|mark|q|rb|rp|rt|rtc|ruby|s|samp|small|span|strong|sub|sup|time|u|var|wbr|area|audio|img|map|track|video|embed|object|param|source|canvas|noscript|script|del|ins|caption|col|colgroup|table|tbody|td|tfoot|th|thead|tr|button|datalist|fieldset|form|input|label|legend|meter|optgroup|option|output|progress|select|textarea|details|dialog|menu|menuitem|summary|content|element|shadow|slot|template|acronym|applet|basefont|big|blink|center|command|content|dir|element|font|frame|frameset|isindex|keygen|listing|marquee|multicol|nextid|noembed|plaintext|shadow|slot|spacer|strike|tt|xmp)[^>]*>',
            re.IGNORECASE
        )
    
    def process_request(self, request):
        # Check for SQL injection in GET parameters
        for key, value in request.GET.items():
            if isinstance(value, str) and self.sql_patterns.search(value):
                return HttpResponseForbidden("Forbidden: Security violation detected")
        
        # Check for XSS in GET parameters
        for key, value in request.GET.items():
            if isinstance(value, str) and self.xss_patterns.search(value):
                return HttpResponseForbidden("Forbidden: Security violation detected")
        
        # For POST requests, check form data
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str):
                    # Check for SQL injection
                    if self.sql_patterns.search(value):
                        return HttpResponseForbidden("Forbidden: Security violation detected")
                    
                    # Check for XSS
                    if self.xss_patterns.search(value):
                        return HttpResponseForbidden("Forbidden: Security violation detected")
        
        return None

class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """
    Middleware to add Content-Security-Policy headers
    """
    def process_response(self, request, response):
        # Add CSP headers
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
        )
        
        # Add other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response