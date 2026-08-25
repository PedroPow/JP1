import discord
from discord import app_commands, ui
from discord.ext import commands
import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv
import asyncio
import io
import aiohttp
from discord.ui import Modal, TextInput

load_dotenv()

# --- CONFIGURAÇÕES DE INTENÇÕES (CORRIGIDO E MANTIDO) ---
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # <-- Mantido ativo para o on_member_join funcionar

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
CARGO_VISITANTE_ID = 1502777759863144520
CARGO_ANALISE_ID = 1502777759863144523
CARGO_CRIADOR_ID = 1502777759863144526

LOGS = {
    "cadastro": 1514848008745914438, "aceite": 1514848072943931414, "recusa": 1502777767610155128,
    "promocao": 1514848245707440350, "comandos": 1502777767610155131, "clearall": 1502777767610155131,
    "mensagem": 1502777767610155131, "adv": 1514856053987213443, "ban": 1514856110740213921
}

ID_CARGO_ADV1 = 1514862629401788557  
ID_CARGO_ADV2 = 1514862551916351518  
ID_CARGO_ADV3 = 1514862700658688112  
ID_CARGO_BANIDO = 1514862792468074526 

CARGO_STAFF_ID = 1502777759880188125

DOMINIOS_PLATAFORMAS = (
    "tiktok.com", "instagram.com", "youtube.com", "youtu.be",
    "kick.com", "facebook.com", "kwai.com", "twitch.tv"
)

def link_plataforma_valido(link: str) -> bool:
    link = link.strip()
    if not link:
        return False

    url = urlparse(link if "://" in link else f"https://{link}")
    hostname = (url.hostname or "").lower().rstrip(".")
    return any(hostname == dominio or hostname.endswith(f".{dominio}") for dominio in DOMINIOS_PLATAFORMAS)

async def enviar_log(guild, tipo, titulo, description, cor=discord.Color.red()):
    canal_id = LOGS.get(tipo)
    if not canal_id: return
    canal = guild.get_channel(canal_id)
    if not canal: return

    embed = discord.Embed(title=titulo, description=description, color=cor, timestamp=discord.utils.utcnow())
    embed.set_footer(text="Jardim Peri RP • Sistema de Logs")
    await canal.send(embed=embed)

# --- INTERFACES DO USUÁRIO (UI) ---

# CLASSE QUE ESTAVA FALTANDO DECLARAR:
class MenuGerenciamentoTicket(ui.View):
    def __init__(self, nome_usuario=""):
        super().__init__(timeout=None)
        self.add_item(SelectAcoes(nome_usuario))

class FormularioSetModal(ui.Modal, title="Solicitação de Set"):
    nome_usuario = ui.TextInput(label="Nome Completo", placeholder="Ex: pow-ehrmantraut", min_length=5, max_length=20)
    discord_id = ui.TextInput(label="Identificação (ID)", placeholder="Ex: 37", min_length=1, max_length=300)
    link_plataforma = ui.TextInput(label="Link da Plataforma", placeholder="Ex: twitch.tv/... ou youtube.com/...")
    observacao = ui.TextInput(label="Observação (Opcional)", style=discord.TextStyle.paragraph, required=False, max_length=300)

    async def on_submit(self, interaction: discord.Interaction):        
        link_digitado = self.link_plataforma.value
        
        if not link_plataforma_valido(link_digitado):
            embed_erro = discord.Embed(
                description="⚠️ Link inválido! Use apenas links de plataformas permitidas (TikTok, Instagram, YouTube, Kick, Facebook, Kwai ou Twitch).", 
                color=0xFF0000
            )
            return await interaction.response.send_message(embed=embed_erro, ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        categoria_inicial = guild.get_channel(CATEGORIA_TICKET_INICIAL)
        channel_name = f"🎟️・{self.nome_usuario.value.lower()}"
        
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=categoria_inicial,
            reason=f"Ticket de Set aberto por {interaction.user.name}"
        )
        
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        await enviar_log(
            guild,
            "cadastro",
            "Novo Cadastro Aberto",
            f"\nUsuário:\n{interaction.user.mention}\n\nNome:\n`{self.nome_usuario.value}`\n\nID:\n`{self.discord_id.value}`\n\nPlataforma:\n{self.link_plataforma.value}\n\n🎫 Ticket:\n{ticket_channel.mention}\n"
        )        

        # --- EMBED DO TICKET ---
        embed = discord.Embed(title="<:emojiJP:1505074670829961236> Contrato Recebido", color=discord.Color.red())
        embed.description = f"Membro: **{interaction.user.mention}**\n"
        embed.add_field(name="Nome Completo:", value=f"`{self.nome_usuario.value}`", inline=True)
        embed.add_field(name="Identificação (ID):", value=f"`{self.discord_id.value}`", inline=True)
        embed.add_field(name="Link da Plataforma:", value=f"{self.link_plataforma.value}", inline=False)
        embed.add_field(name="Observação:", value=f"`{self.observacao.value}`" if self.observacao.value else "`Nenhuma observação informada.`", inline=False)
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1505098549610811462/Criadores_JP_2.png")
        embed.set_footer(text="Jardim Peri RP - Todos os direitos reservados", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp")

        await ticket_channel.send(embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario.value))   
        
        # --- EMBED DE SUCESSO ---
        embed_sucesso = discord.Embed(
            title="🎫 Ticket Criado com Sucesso!",
            description="Seu formulário foi enviado. Clique no botão abaixo para ir direto ao seu ticket de atendimento.",
            color=discord.Color.red()
        )
        
        view_redirecionamento = ui.View()
        view_redirecionamento.add_item(ui.Button(
            label="Ir para o Ticket", 
            url=ticket_channel.jump_url, 
            style=discord.ButtonStyle.red,
            emoji="<:emojiJP:1505074670829961236>"
        ))
        
        await interaction.followup.send(embed=embed_sucesso, view=view_redirecionamento, ephemeral=True)

        cargo_analise = guild.get_role(CARGO_ANALISE_ID)
        if cargo_analise:
            try: await interaction.user.add_roles(cargo_analise)
            except discord.Forbidden: print("Bot sem permissão para aplicar o cargo Em Análise.")        

class BotaoSolicitarSet(ui.View):
    def __init__(self): super().__init__(timeout=None)

    @ui.button(label="Abrir Cadastro", style=discord.ButtonStyle.gray, emoji="<:emojiJP:1505074670829961236>", custom_id="btn_solicitar_set")
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
                ids_cargos = CARGOS.get(nivel, [])
                cargos_para_adicionar = [guild.get_role(c_id) for c_id in ids_cargos if guild.get_role(c_id)]
                if cargos_para_adicionar:
                    try: await membro.add_roles(*cargos_para_adicionar)
                    except discord.Forbidden: print("Bot sem permissão para aplicar os cargos do Set.")

                cargos_para_remover = []
                cargo_visitante = guild.get_role(CARGO_VISITANTE_ID)
                cargo_analise = guild.get_role(CARGO_ANALISE_ID)
                if cargo_visitante and cargo_visitante in membro.roles: cargos_para_remover.append(cargo_visitante)
                if cargo_analise and cargo_analise in membro.roles: cargos_para_remover.append(cargo_analise)
                if cargos_para_remover:
                    try: await membro.remove_roles(*cargos_para_remover)
                    except discord.Forbidden: print("Bot sem permissão para remover cargos antigos.")

                novo_apelido = f"{EMOJIS[nivel]} | {nome_modal}"
                if len(novo_apelido) > 32: novo_apelido = novo_apelido[:31] + "…"
                try: await membro.edit(nick=novo_apelido)
                except discord.Forbidden: print(f"Bot sem permissão para alterar o apelido de {membro.name}.")

        await channel.edit(name=f"{EMOJIS[nivel]}・{nome_modal.lower()}")
        id_categoria = CATEGORIAS.get(nivel)
        if id_categoria:
            nova_categoria = guild.get_channel(id_categoria)
            if nova_categoria: await channel.edit(category=nova_categoria)

        for i, field in enumerate(embed.fields):
            if field.name.startswith("🎁 Benefícios"):
                embed.remove_field(i)
                break

        texto_beneficios = "\n".join(BENEFICIOS[nivel])
        embed.add_field(name=f"🎁 Benefícios - Nível {nivel.capitalize()}", value=texto_beneficios, inline=False)
        embed.color = discord.Color.red()

        await mensagem.edit(content=None, embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario))

        if match and membro:
            embed_dm = discord.Embed(
                title="<:emojiJP:1505074670829961236> Atualização no seu Set de Streamer!",
                description=f"Olá {membro.mention}, seu set no servidor foi atualizado com sucesso!",
                color=discord.Color.red()
            )
            embed_dm.add_field(name="Novo Status:", value=f"**`{nivel.capitalize()}` `{EMOJIS[nivel]}`**.", inline=False)
            embed_dm.add_field(name="🎁 Benefícios Liberados:", value=texto_beneficios, inline=False)
            embed_dm.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif")
            embed_dm.set_footer(text="Parabéns e boa sorte com o seu conteúdo!", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp")
            
            try: await membro.send(embed=embed_dm)
            except discord.Forbidden: print("DM Fechada.")

            if self.acao == "aceitar":
                await enviar_log(guild, "aceite", "✅ NOVO CRIADOR ACEITO", 
                    f"\n👮 Staff:\n{interaction.user.mention}\n\n🎥 Criador:\n{membro.mention}\n\n🏷️ Nível:\n{EMOJIS[nivel]} **{nivel.upper()}**\n\n📅 Data:\n<t:{int(discord.utils.utcnow().timestamp())}:F>\n")
            elif self.acao == "promover":
                await enviar_log(guild, "promocao", "📈 CRIADOR PROMOVIDO / REBAIXADO", 
                    f"\n👮 Staff:\n{interaction.user.mention}\n\n🎥 Criador:\n{membro.mention}\n\n🏷️ Novo nível:\n{EMOJIS[nivel]} **{nivel.upper()}**\n\nCanal:\n{interaction.channel.mention}\n")

class SelectAcoes(ui.Select):
    def __init__(self, nome_usuario=""):
        self.nome_usuario = nome_usuario
        options = [
            discord.SelectOption(label="Aceitar", value="aceitar", description="Aprovar solicitação e escolher nível", emoji="<:AMARELO:1505086398309470288>"),
            discord.SelectOption(label="Recusar", value="recusar", description="Fechar/Recusar o ticket", emoji="<:x1:1505086332936917042>"),
            discord.SelectOption(label="Promover/Rebaixar", value="promover", description="Mudar o nível atual do usuário", emoji="<:ADD:1505086562508214472>")
        ]
        super().__init__(placeholder="⚙️・Painel Administrativo", min_values=1, max_values=1, options=options, custom_id="select_acoes_ticket")

    # CORREÇÃO DE INDENTAÇÃO AQUI (A FUNÇÃO FOI ENTRADA PARA DENTRO DA CLASSE):
    async def callback(self, interaction: discord.Interaction):
        CARGO_STAFF_ID = 1502777759880188125
        if not any(role.id == CARGO_STAFF_ID for role in interaction.user.roles):
            embed_negado = discord.Embed(
                title="🔒 Acesso Negado",
                description="Apenas membros da Staff autorizados podem gerenciar este ticket.\n Cargo necessário: <@&1502777759880188125>",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed_negado, ephemeral=True)
        
        acao = self.values[0]
        guild = interaction.guild
        nome_atual = self.nome_usuario
        if not nome_atual:
            if "solicitação-" in interaction.channel.name: nome_atual = interaction.channel.name.split("solicitação-")[-1]
            elif "・" in interaction.channel.name: nome_atual = interaction.channel.name.split("・")[-1]
            else: nome_atual = interaction.channel.name

        if acao in ["aceitar", "promover"]:
            view_niveis = ui.View()
            view_niveis.add_item(SelectNiveis(nome_atual, acao))
            await interaction.response.edit_message(content=f"Selecione o nível para o qual deseja {acao}:", view=view_niveis)
            
        elif acao == "recusar":
            embed_recusado = discord.Embed(
                title="❌ Solicitação Recusada",
                description="Este ticket foi fechado pela administração e o canal será deletado em **5 segundos**.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_recusado)

            embed_ticket = interaction.message.embeds[0]
            match_recusa = re.search(r"<@!?(\d+)>", embed_ticket.description)
            membro = None
            membro_saiu = False

            if match_recusa:
                membro_id = int(match_recusa.group(1))
                try:
                    membro = guild.get_member(membro_id) or await guild.fetch_member(membro_id)
                except discord.NotFound:
                    membro_saiu = True
                except Exception:
                    membro_saiu = True

                if membro and not membro_saiu:
                    cargos_remover = []
                    for nivel, ids in CARGOS.items():
                        for cargo_id in ids:
                            cargo = guild.get_role(cargo_id)
                            if cargo and cargo in membro.roles:
                                cargos_remover.append(cargo)

                    CARGO_CRIADOR_ID = 1502777759683144526
                    cargo_criador = guild.get_role(CARGO_CRIADOR_ID)
                    if cargo_criador and cargo_criador in membro.roles:
                        cargos_remover.append(cargo_criador)

                    cargo_analise = guild.get_role(CARGO_ANALISE_ID)
                    if cargo_analise and cargo_analise in membro.roles:
                        cargos_remover.append(cargo_analise)

                    if cargos_remover:
                        try: await membro.remove_roles(*cargos_remover)
                        except discord.Forbidden: print("Sem permissão para remover cargos.")

                    cargo_visitante = guild.get_role(CARGO_VISITANTE_ID)
                    if cargo_visitante:
                        try: await membro.add_roles(cargo_visitante)
                        except discord.Forbidden: pass

                    try: await membro.edit(nick=None)
                    except discord.Forbidden: print("Sem permissão para alterar nick.")

                    try:
                        embed_dm_recusa = discord.Embed(
                            title="❌ Set de Streamer Recusado",
                            description=f"Olá {membro.mention},\n\nSua solicitação de Set de Streamer foi recusada pela administração.",
                            color=discord.Color.red()
                        )
                        await membro.send(embed=embed_dm_recusa)
                    except Exception: pass

            if membro_saiu:
                await enviar_log(
                    guild, "recusa", "❌ Ticket Fechado (Membro Saiu)",
                    f"Staff:\n{interaction.user.mention}\n\nNota:\n`O usuário não se encontra mais no servidor. O canal foi limpo e os procedimentos de cargos foram pulados.`"
                )
            else:
                await enviar_log(
                    guild, "recusa", "❌ Criador Recusado",
                    f"Staff:\n{interaction.user.mention}\n\nUsuário:\n{membro.mention if membro else 'Não encontrado'}\n\nAções realizadas:\n\n❌ Cargos de nível removidos\n❌ Cargo criador removido\n❌ Cargo em análise removido\n🔄 Nick restaurado\n👤 Cargo visitante aplicado"
                )

            await asyncio.sleep(5)
            try: await interaction.channel.delete()
            except Exception as e: print(f"Erro ao deletar canal: {e}")

# --- COMANDOS E EVENTOS DE INICIALIZAÇÃO ---

@bot.event
async def on_ready():
    print(f"Bot logado com sucesso como {bot.user}")
    bot.add_view(BotaoSolicitarSet())
    bot.add_view(MenuGerenciamentoTicket())
    
    try:
        synced = await bot.tree.sync()
        print(f"📌 {len(synced)} comandos de barra (/) sincronizados globalmente!")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")
        
    print("📌 Todas as Views Persistentes foram carregadas com sucesso!")

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    cargo_visitante = guild.get_role(CARGO_VISITANTE_ID)
    if cargo_visitante:
        try:
            await member.add_roles(cargo_visitante)
            print(f"Cargo Visitante aplicado automaticamente para {member.name}.")
        except discord.Forbidden:
            print(f"Bot sem permissão para dar cargo de Visitante para {member.name}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def JP1(ctx):
    embed = discord.Embed(
        title="<:emojiJP:1505074670829961236> Jardim Peri - **CADASTRO DE STREAMERS**",
        description="> Seja bem-vindo ao painel de **CADASTRO DE STREAMERS**!\n\n> clique no botão abaixo e preencha o formulário com suas informações.\n\n> Nossa equipe irá analisar sua solicitação e entrar em contato o mais breve possível.\n\n> Obrigado por escolher o Jardim Peri!\n\n**Tenha em mãos as seguintes informações para agilizar sua solicitação:**\n\n🔸`Nome Completo`\n🔸`Identificação (ID)`\n🔸`Link da Plataforma`\n🔸`Observação (Opcional)`\n",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif")
    embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1505098549610811462/Criadores_JP_2.png")
    embed.set_footer(text="Jardim Peri RP - Todos os direitos reservados", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp")

    await ctx.send(embed=embed, view=BotaoSolicitarSet())
    await enviar_log(ctx.guild, "comandos", "Painel Criado", f"\nQuem usou:\n{ctx.author.mention}\n\nComando:\n`!JP1`\n\nCanal:\n{ctx.channel.mention}\n")

@bot.tree.command(name="clearall", description="Apaga mensagens do canal.")
async def clearall(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    canal = interaction.channel
    await interaction.response.send_message("🧹 Limpando canal...", ephemeral=True)
    mensagens = await canal.purge()
    await enviar_log(interaction.guild, "clearall", "🧹 CLEARALL USADO", f"\nUsuário:\n{interaction.user.mention}\n\nID:\n`{interaction.user.id}`\n\nCanal:\n{canal.mention}\n\nMensagens apagadas:\n`{len(mensagens)}`\n", discord.Color.orange())

@bot.tree.command(name="adv", description="Aplica advertência acumulativa em um membro.")
async def adv(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not any(role.id == CARGO_STAFF_ID for role in interaction.user.roles) and not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ Você não tem permissão para aplicar advertências.", ephemeral=True)

    guild = interaction.guild
    adv1 = guild.get_role(ID_CARGO_ADV1)
    adv2 = guild.get_role(ID_CARGO_ADV2)
    adv3 = guild.get_role(ID_CARGO_ADV3)
    banido = guild.get_role(ID_CARGO_BANIDO)

    if not all([adv1, adv2, adv3]):
        return await interaction.response.send_message("❌ Erro: Um ou mais cargos de advertência não foram encontrados no servidor.", ephemeral=True)

    try:
        if banido and banido in membro.roles:
            return await interaction.response.send_message("⚠️ Esse membro já possui o cargo de banido.", ephemeral=True)

        if adv3 in membro.roles:
            await membro.remove_roles(adv3)
            if banido: await membro.add_roles(banido)
            msg = "🚫 **4ª advertência** → Membro punido com o cargo de Banido!"
            cor_log = discord.Color.gold()
        elif adv2 in membro.roles:
            await membro.remove_roles(adv2)
            await membro.add_roles(adv3)
            msg = "⚠️ **3ª advertência** aplicada com sucesso!"
            cor_log = discord.Color.gold()
        elif adv1 in membro.roles:
            await membro.remove_roles(adv1)
            await membro.add_roles(adv2)
            msg = "⚠️ **2ª advertência** aplicada com sucesso!"
            cor_log = discord.Color.gold()
        else:
            await membro.add_roles(adv1)
            msg = "⚠️ **1ª advertência** aplicada com sucesso!"
            cor_log = discord.Color.gold()

        await interaction.response.send_message(msg, ephemeral=True)
        texto_log = f"\n**Staff:**\n{interaction.user.mention}\n\n**Membro:**\n{membro.mention}\n\n**Motivo:**\n{motivo}\n"
        await enviar_log(guild, "adv", "⚠️ ADVERTÊNCIA APLICADA", texto_log, cor_log)

    except discord.Forbidden:
        return await interaction.response.send_message("❌ O bot não tem permissão de gerenciamento de cargos.", ephemeral=True)
    except Exception as e:
        print(f"Erro no comando adv: {e}")
        return await interaction.response.send_message("❌ Ocorreu um erro interno.", ephemeral=True)

@bot.tree.command(name="ban", description="Banir membro")
async def ban(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await membro.ban(reason=motivo)
    await interaction.response.send_message(f"⛔ {membro.mention} banido!", ephemeral=True)
    await enviar_log(interaction.guild, "ban", "⛔ MEMBRO BANIDO", f"\nStaff:\n{interaction.user.mention}\n\nBanido:\n{membro.mention}\n\nID:\n`{membro.id}`\n\nMotivo:\n{motivo}\n", discord.Color.red())

class MensagemModal(Modal, title="📢 Enviar Mensagem"):
    conteudo = TextInput(label="Conteúdo da mensagem", style=discord.TextStyle.paragraph, required=True, max_length=2000)

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)
        
        await interaction.response.send_message("⏳ Enviando...", ephemeral=True)
        try:
            msg_inicial = await interaction.channel.send(self.conteudo.value)
        except Exception:
            return await interaction.followup.send("❌ Não consegui enviar a mensagem inicial.", ephemeral=True)
            
        await interaction.followup.send("📎 Responda aquela mensagem com anexos em até 5 minutos.", ephemeral=True)

        def check(m: discord.Message):
            return (m.reference and m.reference.message_id == msg_inicial.id and m.author == interaction.user and m.channel == interaction.channel)

        try:
            reply = await bot.wait_for("message", timeout=300.0, check=check)
            files = []
            async with aiohttp.ClientSession() as session:
                for a in reply.attachments:
                    try:
                        async with session.get(a.url) as resp:
                            dados = await resp.read()
                            files.append(discord.File(io.BytesIO(dados), filename=a.filename))
                    except Exception: continue

            try:
                await msg_inicial.delete()
                await reply.delete()
            except Exception: pass

            try:
                await interaction.channel.send(content=self.conteudo.value, files=files)
                await enviar_log(interaction.guild, "mensagem", "📢 MENSAGEM ENVIADA", f"\nStaff:\n{interaction.user.mention}\n\nCanal:\n{interaction.channel.mention}\n\nMensagem:\n\n{self.conteudo.value}\n", discord.Color.blue())
            except Exception:
                await interaction.followup.send("❌ Erro ao reenviar mensagem.", ephemeral=True)
        except asyncio.TimeoutError:
            try: await interaction.followup.send("⏰ Tempo esgotado. Nenhum anexo recebido.", ephemeral=True)
            except Exception: pass

@bot.tree.command(name="mensagem", description="Enviar mensagem como bot")
async def mensagem(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
    await interaction.response.send_modal(MensagemModal())

bot.run(TOKEN)