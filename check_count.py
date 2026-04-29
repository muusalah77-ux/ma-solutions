from supabase import create_client

URL = "https://rsqzdzgjdoavhxbbpelx.supabase.co"
KEY = "sb_secret_Hdvq3VDFnR-EUwoebK5pRQ_GoL2B5ff"
supabase = create_client(URL, KEY)

res = supabase.table("employees").select("id", count="exact").execute()
print(f"Total Employees Count: {res.count}")
