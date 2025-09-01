// src/lib/supabaseClient.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ixmgvsqqyvjlnlhhgrsx.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4bWd2c3FxeXZqbG5saGhncnN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzOTYzNjMsImV4cCI6MjA3MTk3MjM2M30.VfV4Yger6ibezX2V1o-VWxNFfeYoP_ag5nzmIsjm0n8'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)