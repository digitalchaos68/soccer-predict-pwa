import requests

url = "https://ixmgvsqqyvjlnlhhgrsx.supabase.co/rest/v1/predictions"
headers = {
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4bWd2c3FxeXZqbG5saGhncnN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzOTYzNjMsImV4cCI6MjA3MTk3MjM2M30.VfV4Yger6ibezX2V1o-VWxNFfeYoP_ag5nzmIsjm0n8",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4bWd2c3FxeXZqbG5saGhncnN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzOTYzNjMsImV4cCI6MjA3MTk3MjM2M30.VfV4Yger6ibezX2V1o-VWxNFfeYoP_ag5nzmIsjm0n8"
}

response = requests.get(url, headers=headers)
print(response.status_code, response.text)