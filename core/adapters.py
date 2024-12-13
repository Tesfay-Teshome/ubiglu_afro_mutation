from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        url = super().get_connect_redirect_url(request, socialaccount)
        if url.startswith('https://'):
            url = 'http://' + url[8:]
        return url
