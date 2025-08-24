from supabase import create_client, Client

# 🔑 Récupérés depuis Supabase (Settings > API)
SUPABASE_URL = "https://bfhoufgtxshopuemsnyx.supabase.co"  # remplace par ton URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJmaG91Zmd0eHNob3B1ZW1zbnl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5Nzg5OTMsImV4cCI6MjA3MTU1NDk5M30.wVkbgkRTGt9dlg_f3v7hIb6cDXLjd4yGl-xL0sXiptM"  # remplace par ta clé anon

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

