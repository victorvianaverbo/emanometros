-- Press Control — tabela de leads
-- Rode UMA VEZ no Supabase: Dashboard > SQL Editor > New query > cole tudo > Run

create table if not exists public.leads (
  id          bigint generated always as identity primary key,
  created_at  timestamptz not null default now(),
  nome        text not null,
  telefone    text not null,
  produto     text,
  specs       text,
  mensagem    text,
  pagina      text
);

-- Liga Row Level Security
alter table public.leads enable row level security;

-- anon (site público) PODE inserir, mas NÃO pode ler os leads.
-- Leitura só pelo painel/service_role — protege os dados dos clientes.
create policy "anon pode inserir leads"
  on public.leads
  for insert
  to anon
  with check (true);
