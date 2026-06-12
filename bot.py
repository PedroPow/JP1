import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import re
from dotenv import load_dotenv
import asyncio
import io
import aiohttp
from discord.ui import Modal, TextInput

load_dotenv()

# --- CONFIGURAÇÕES DE INTENÇÕES (CORRIGIDO) ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # <-- ATIVADO: Necessário para o on_member_join e gerenciamento de cargos

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN_JP")

# --- CONFIGURAÇÕES FORNECIDAS ---
BENEFICIOS = {
    "bronze": ["🔸`HONDA CB 2020 OU NISSAN VERSA`", "🔸`$20.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER BRONZE`", "🔸`/SOM POR 30 DIAS`"],
    "prata": ["🔸`VW GOLF OU HONDA XRE`", "🔸`$45.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER PRATA`", "🔸`SALÁRIO STREAMER DE 3.500 A CADA 30 MINUTOS`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`"],
    "ouro": ["🔸`CHEVROLET SPIN + HONDA CB 2020`", "🔸`$60.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER OURO`", "🔸`SALÁRIO STREAMER DE 4.500 A CADA 30 MINUTOS`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`"],
    "platina": ["🔸`CHEVROLET SPIN + VW GOLF  + HONDA XRE`", "🔸`$80.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER PLATINA`", "🔸`SALÁRIO STREAMER DE 5.500 A CADA 30 MINUTOS`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`"],
    "esmeralda": ["🔸`BMW M4 + FIAT PALIO + HONDA XRE`", "🔸`$100.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER ESMERALDA`", "🔸`SALÁRIO STREAMER DE 6.500 A CADA 30 MINUTOS`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`", "🔸`/BARBEARIA`"],
    "ruby": ["🔸`SKINSHOP PRÓPRIA`", "🔸`3 VEÍCULOS PERMANENTES DA CONCESSIONÁRIA`", "🔸`$130.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER RUBY`", "🔸`SALÁRIO STREAMER DE 8.500 A CADA 30 MINUTOS`", "🔸`/BARBEARIA`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`"],
    "diamante": ["🔸`SKINSHOP PRÓPRIA`", "🔸`3 VEÍCULOS PERMANENTES DA CONCESSIONÁRIA`", "🔸`$160.000 EM DINHEIRO`", "🔸`TAG EXCLUSIVA STREAMER RUBY`", "🔸`SALÁRIO STREAMER DE 10.000 A CADA 30 MINUTOS`", "🔸`/BARBEARIA`", "🔸`/CAM POR 30 DIAS`", "🔸`/SOM POR 30 DIAS`"],
    "oficial": ["🔸`UM PLANO TOTALMENTE EXCLUSIVO, CRIADO SOB MEDIDA DE ACORDO COM SUAS MÉTRICAS, ALCANCE E DESEMPENHO DENTRO DA CIDADE.`\n 🔸`INCLUINDO BENEFÍCIOS PERSONALIZADOS, VANTAGENS ÚNICAS E RECONHECIMENTO DENTRO DA CIDADE.`"],
}

CATEGORIAS = {
    "bronze": 1502777768058814513, "prata": 1502777768306544640, "ouro": 1502777768306544641, "platina": 1502777768306544642,
    "esmeralda": 1502777768306544643, "ruby": 1502777768306544644, "diamante": 1502777768306544645, "oficial": 1502777768306544646
}

EMOJIS = {
    "bronze": "🔴", "prata": "⚪", "ouro": "🟡", "platina": "🔵", "esmeralda": "🟢", "ruby": "🟠", "diamante": "🟣", "oficial": "⚫"
}

CARGOS = {
    "bronze": [1502777759863144527, 1502777759863144526], "prata": [1502777759880188117, 1502777759863144526],
    "ouro": [1502777759880188118, 1502777759863144526], "platina": [1502777759880188119, 1502777759863144526],
    "esmeralda": [1502777759880188120, 1502777759863144526], "ruby": [1502777759880188121, 1502777759863144526],
    "diamante": [1502777759880188122, 1502777759863144526], "oficial": [1502777759880188123, 1502777759863144526]
}

CATEGORIA_TICKET_INICIAL = 1502777767610155133 
CARGO_VISITANTE_ID = 1502777767610155126
CARGO_ANALISE_ID = 1502777759863144523

LOGS = {
    "cadastro": 1514848008745914438, "aceite": 1514848072943931414, "recusa": 1502777767610155128,
    "promocao": 1514848245707440350, "comandos": 1502777767610155131, "clearall": 1502777767610155131,
    "mensagem": 1502777767610155131, "adv": 1514856053987213443, "ban": 1514856110740213921
}

RE_PLATAFORMAS = re.compile(r'(tiktok\.com|instagram\.com|youtube\.com|youtu\.be|kick\.com|facebook\.com|kwai)', re.IGNORECASE)

async def enviar_log(guild, tipo, titulo, description, cor=discord.Color.red()):
    canal_id = LOGS.get(tipo)
    if not canal_id: return
    canal = guild.get_channel(canal_id)
    if not canal: return

    embed = discord.Embed(title=titulo, description=description, color=cor, timestamp=discord.utils.utcnow())
    embed.set_footer(text="Jardim Peri RP • Sistema de Logs")
    await canal.send(embed=embed)

# --- INTERFACES DO USUÁRIO (UI) ---

class FormularioSetModal(ui.Modal, title="Solicitação de Set"):
    nome_usuario = ui.TextInput(label="Nome Completo", placeholder="Ex: pow-ehrmantraut", min_length=5, max_length=20)
    discord_id = ui.TextInput(label="Identificação (ID)", placeholder="Ex: 37", min_length=1, max_length=300)
    link_plataforma = ui.TextInput(label="Link da Plataforma", placeholder="Ex: youtube.com/...")
    observacao = ui.TextInput(label="Observação (Opcional)", style=discord.TextStyle.paragraph, required=False, max_length=300)

    async def on_submit(self, interaction: discord.Interaction):        
        link_digitado = self.link_plataforma.value
        if not RE_PLATAFORMAS.search(link_digitado):
            embed_erro = discord.Embed(description="⚠️ Link inválido! Use apenas links de plataformas permitidas.", color=0xFF0000)
            return await interaction.response.send_message(embed=embed_erro, ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        categoria_inicial = guild.get_channel(CATEGORIA_TICKET_INICIAL)
        channel_name = f"🎟️・{self.nome_usuario.value.lower()}"
        
        ticket_channel = await guild.create_text_channel(name=channel_name, category=categoria_inicial)
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        await enviar_log(guild, "cadastro", "Novo Cadastro Aberto", 
            f"Usuário: {interaction.user.mention}\nNome: `{self.nome_usuario.value}`\nID: `{self.discord_id.value}`\nPlataforma: {self.link_plataforma.value}\n🎫 Ticket: {ticket_channel.mention}")

        embed = discord.Embed(title="<:emojiJP:1505074670829961236> Contrato Recebido", color=discord.Color.red())
        embed.description = f"Membro: **{interaction.user.mention}**\n"
        embed.add_field(name="Nome Completo:", value=f"`{self.nome_usuario.value}`", inline=True)
        embed.add_field(name="Identificação (ID):", value=f"`{self.discord_id.value}`", inline=True)
        embed.add_field(name="Link da Plataforma:", value=f"{self.link_plataforma.value}", inline=False)
        embed.add_field(name="Observação:", value=f"`{self.observacao.value}`" if self.observacao.value else "`Nenhuma observação informada.`", inline=False)
        
        await ticket_channel.send(embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario.value))   
        
        embed_sucesso = discord.Embed(title="🎫 Ticket Criado com Sucesso!", description="Seu formulário foi enviado.", color=discord.Color.red())
        view_redirecionamento = ui.View()
        view_redirecionamento.add_item(ui.Button(label="Ir para o Ticket", url=ticket_channel.jump_url, style=discord.ButtonStyle.red))
        await interaction.followup.send(embed=embed_sucesso, view=view_redirecionamento, ephemeral=True)

        cargo_analise = guild.get_role(CARGO_ANALISE_ID)
        if cargo_analise:
            try: await interaction.user.add_roles(cargo_analise)
            except discord.Forbidden: print("Bot sem permissão para aplicar o cargo Em Análise.")        

class BotaoSolicitarSet(ui.View):
    def __init__(self): super().__init__(timeout=None)
    @ui.button(label="Abrir Cadastro", style=discord.ButtonStyle.gray, custom_id="btn_solicitar_set")
    async def solicitar_set(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(FormularioSetModal())

class SelectNiveis(ui.Select):
    def __init__(self, nome_usuario, acao):
        self.nome_usuario = nome_usuario
        self.acao = acao
        options = [discord.SelectOption(label=nivel.capitalize(), value=nivel, emoji=EMOJIS[nivel]) for nivel in BENEFICIOS.keys()]
        super().__init__(placeholder="⚙️・Gerenciar nível", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        nivel = self.values[0]
        guild = interaction.guild
        channel = interaction.channel
        mensagem = interaction.message
        embed = mensagem.embeds[0]

        nome_modal = self.nome_usuario
        match = re.search(r"<@!?(\d+)>", embed.description)
        
        if match:
            membro_id = int(match.group(1))
            try: membro = guild.get_member(membro_id) or await guild.fetch_member(membro_id)
            except Exception: membro = None
            
            if membro:
                # Cargos
                ids_cargos = CARGOS.get(nivel, [])
                cargos_para_adicionar = [guild.get_role(c_id) for c_id in ids_cargos if guild.get_role(c_id)]
                if cargos_para_adicionar:
                    try: await membro.add_roles(*cargos_para_adicionar)
                    except discord.Forbidden: print("Bot sem permissão para aplicar os cargos.")

                # Remover Antigos
                cargos_para_remover = [guild.get_role(r_id) for r_id in [CARGO_VISITANTE_ID, CARGO_ANALISE_ID] if guild.get_role(r_id) and guild.get_role(r_id) in membro.roles]
                if cargos_para_remover:
                    try: await membro.remove_roles(*cargos_para_remover)
                    except discord.Forbidden: print("Erro ao remover cargos antigos.")

                # Nickname
                novo_apelido = f"{EMOJIS[nivel]} | {nome_modal}"
                if len(novo_apelido) > 32: novo_apelido = novo_apelido[:31] + "…"
                try: await membro.edit(nick=novo_apelido)
                except discord.Forbidden: print("Sem permissão para alterar apelido.")

        await channel.edit(name=f"{EMOJIS[nivel]}・{nome_modal.lower()}")
        id_categoria = CATEGORIAS.get(nivel)
        if id_categoria:
            nova_cat = guild.get_channel(id_categoria)
            if nova_cat: await channel.edit(category=nova_cat)

        for i, field in enumerate(embed.fields):
            if field.name.startswith("🎁 Benefícios"):
                embed.remove_field(i)
                break

        texto_beneficios = "\n".join(BENEFICIOS[nivel])
        embed.add_field(name=f"🎁 Benefícios - Nível {nivel.capitalize()}", value=texto_beneficios, inline=False)
        await mensagem.edit(content=None, embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario))

        if match and membro:
            embed_dm = discord.Embed(title="Atualização no seu Set!", description=f"Olá {membro.mention}, seu set foi atualizado!", color=discord.Color.red())
            embed_dm.add_field(name="Novo Status:", value=f"**{nivel.capitalize()} {EMOJIS[nivel]}**")
            try: await membro.send(embed=embed_dm)
            except discord.Forbidden: print("DM fechada.")

            tipo_log = "aceite" if self.acao == "aceitar" else "promocao"
            tit_log = "✅ NOVO CRIADOR ACEITO" if self.acao == "aceitar" else "📈 CRIADOR PROMOVIDO / REBAIXADO"
            await enviar_log(guild, tipo_log, tit_log, f"Staff: {interaction.user.mention}\nCriador: {membro.mention}\nNível: {EMOJIS[nivel]} {nivel.upper()}")

class SelectAcoes(ui.Select):
    def __init__(self, nome_usuario=""):
        self.nome_usuario = nome_usuario
        options = [
            discord.SelectOption(label="Aceitar", value="aceitar", description="Aprovar solicitação", emoji="✅"),
            discord.SelectOption(label="Recusar", value="recusar", description="Fechar/Recusar o ticket", emoji="❌"),
            discord.SelectOption(label="Promover/Rebaixar", value="promover", description="Mudar o nível", emoji="📈")
        ]
        super().__init__(placeholder="⚙️・Painel Administrativo", min_values=1, max_values=1, options=options, custom_id="select_acoes_ticket")

    async def callback(self, interaction: discord.Interaction):
        CARGO_STAFF_ID = 1502777759880188125
        if not any(role.id == CARGO_STAFF_ID for role in interaction.user.roles):
            return await interaction.response.send_message("🔒 Acesso Negado.", ephemeral=True)
        
        acao = self.values[0]
        guild = interaction.guild
        nome_atual = self.nome_usuario or interaction.channel.name.split("・")[-1]

        if acao in ["aceitar", "promover"]:
            view_niveis = ui.View()
            view_niveis.add_item(SelectNiveis(nome_atual, acao))
            await interaction.response.edit_message(content=f"Selecione o nível para {acao}:", view=view_niveis)
            
        elif acao == "recusar":
            await interaction.response.send_message("❌ Solicitação Recusada. Deletando canal em 5 segundos...")
            embed_ticket = interaction.message.embeds[0]
            match_recusa = re.search(r"<@!?(\d+)>", embed_ticket.description)
            
            membro = None
            if match_recusa:
                membro_id = int(match_recusa.group(1))
                try:
                    membro = guild.get_member(membro_id) or await guild.fetch_member(membro_id)
                    if membro:
                        embed_dm = discord.Embed(title="❌ Solicitação Recusada", description="Seu Set de Streamer não foi aprovado.", color=discord.Color.red())
                        await membro.send(embed=embed_dm)
                except Exception: print("Erro ao enviar DM de recusa.")

            await enviar_log(guild, "recusa", "❌ NOVO CRIADOR RECUSADO", f"Staff: {interaction.user.mention}\nCriador: {membro.mention if membro else 'Não encontrado'}")
            await interaction.message.delete()
            await asyncio.sleep(5)
            await interaction.channel.delete()

class MenuGerenciamentoTicket(ui.View):
    def __init__(self, nome_usuario=""):
        super().__init__(timeout=None)
        self.add_item(SelectAcoes(nome_usuario))

# --- COMANDOS E EVENTOS (CORRIGIDOS) ---

@bot.event
async def on_ready():
    print(f"Bot logado com sucesso como {bot.user}")
    bot.add_view(BotaoSolicitarSet())
    bot.add_view(MenuGerenciamentoTicket())
    
    # --- NOVO: SINCRONIZA OS COMANDOS COM O DISCORD ---
    try:
        synced = await bot.tree.sync()
        print(f"📌 {len(synced)} comandos de barra (/) sincronizados globalmente!")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")
        
    print("📌 Todas as Views Persistentes foram carregadas!")

@bot.event  # <-- CORRIGIDO: Removido o 'self' pois não está em um Cog
async def on_member_join(member: discord.Member):
    guild = member.guild
    cargo_visitante = guild.get_role(CARGO_VISITANTE_ID)
    if cargo_visitante:
        try:
            await member.add_roles(cargo_visitante)
            print(f"Cargo Visitante aplicado para {member.name}.")
        except discord.Forbidden:
            print("Bot sem permissão para dar cargo.")

@bot.command()
@commands.has_permissions(administrator=True)
async def JP1(ctx):
    embed = discord.Embed(title="Jardim Peri - CADASTRO DE STREAMERS", description="Clique no botão abaixo para iniciar.", color=discord.Color.red())
    await ctx.send(embed=embed, view=BotaoSolicitarSet())
    await enviar_log(ctx.guild, "comandos", "Painel Criado", f"Quem usou: {ctx.author.mention}\nComando: `!JP1`")

@bot.tree.command(name="clearall", description="Apaga mensagens do canal.")
async def clearall(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await interaction.response.send_message("🧹 Limpando canal...", ephemeral=True)
    mensagens = await interaction.channel.purge()
    await enviar_log(interaction.guild, "clearall", "🧹 CLEARALL USADO", f"Staff: {interaction.user.mention}\nMensagens apagadas: `{len(mensagens)}`", discord.Color.orange())

@bot.tree.command(name="adv", description="Aplicar advertência")
async def adv(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await interaction.response.send_message("⚠️ Advertência aplicada!", ephemeral=True)
    await enviar_log(interaction.guild, "adv", "⚠️ ADV APLICADA", f"Staff: {interaction.user.mention}\nMembro: {membro.mention}\nMotivo: {motivo}", discord.Color.yellow())

@bot.tree.command(name="ban", description="Banir membro")
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await membro.ban(reason=motivo)
    await interaction.response.send_message(f"⛔ {membro.mention} banido!", ephemeral=True)
    await enviar_log(interaction.guild, "ban", "⛔ MEMBRO BANIDO", f"Staff: {interaction.user.mention}\nBanido: {membro.mention}\nMotivo: {motivo}", discord.Color.red())

class MensagemModal(Modal, title="Enviar Mensagem"):
    texto = TextInput(label="Mensagem", style=discord.TextStyle.paragraph, max_length=2000)
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.send(self.texto.value)
        await interaction.response.send_message("✅ Mensagem enviada!", ephemeral=True)
        await enviar_log(interaction.guild, "mensagem", "📢 MENSAGEM ENVIADA", f"Staff: {interaction.user.mention}\nMensagem: {self.texto.value}", discord.Color.blue())

@bot.tree.command(name="mensagem", description="Enviar mensagem como bot")
async def mensagem(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await interaction.response.send_modal(MensagemModal())

bot.run(TOKEN)