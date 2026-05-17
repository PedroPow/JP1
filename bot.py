import discord
from discord import app_commands, ui
from discord.ext import commands
import os  # <-- CERTIFIQUE-SE DE QUE ESTA LINHA ESTÁ AQUI
import re
from dotenv import load_dotenv

load_dotenv()

# Configurações de Intenções
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN_JP")  # Certifique-se de definir a variável de ambiente DISCORD_BOT_TOKEN com o token do seu bot

# --- CONFIGURAÇÕES FORNECIDAS ---
BENEFICIOS = {
    "bronze": ["• 18 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $18.000 em dinheiro", "• Direito à aquisição de 01 (um) veículo, desde que disponível para compra com moeda do jogo, com valor máximo de até $175.000"],
    "prata": ["• 25 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $18.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Direito à aquisição de 01 (um) veículo, desde que disponível para compra com moeda do jogo, com valor máximo de até $350.000"],
    "ouro": ["• 32 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $25.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Direito à aquisição de 01 (um) veículo, desde que disponível para compra com moeda do jogo, com valor máximo de até $525.000"],
    "platina": ["• 39 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $32.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Verificação oficial no Instagram", "• Direito à aquisição de 01 (um) veículo disponível na concessionária"],
    "esmeralda": ["• 46 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $39.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Acesso ao /barber", "• Verificação oficial no Instagram", "• Direito à aquisição de 01 (um) veículo disponível na concessionária"],
    "ruby": ["• 53 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $46.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Verificação oficial no Instagram", "• Direito à aquisição de 02 (dois) veículos disponíveis na concessionária", "• Direito a 01 (um) item de até $35 na loja do servidor", "• Acesso ao /barber", "• Acesso à /skin shop"],
    "diamante": ["• 60 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $46.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Verificação oficial no Instagram", "• Direito à aquisição de 02 (três) veículos disponíveis na concessionária", "• Direito a 01 (um) item de até $53 na loja do servidor", "• Acesso ao /barber", "• Acesso à /skin shop"],
    "oficial": ["• 67 Gemas ( Todo dia 1 - Solicitar no Ticket Streamer )", "• $46.000 em dinheiro", "• Acesso ao comando /cam", "• Acesso ao comando /som", "• Acesso ao comando /remap", "• Verificação oficial no Instagram", "• Direito à aquisição de 02 (quatro) veículos disponíveis na concessionária", "• Direito a 01 (um) item de até $70 na loja do servidor", "• Acesso ao /barber", "• Acesso à /skin shop", "• Redução do tempo de morte", "• Acesso ao drone"]
}

CATEGORIAS = {
    "bronze": 1502777768058814513,
    "prata": 1502777768306544640,
    "ouro": 1502777768306544641,
    "platina": 1502777768306544642,
    "esmeralda": 1502777768306544643,
    "ruby": 1502777768306544644,
    "diamante": 1502777768306544645,
    "oficial": 1502777768306544646
}

EMOJIS = {
    "bronze": "🔴", "prata": "⚪", "ouro": "🟡", "platina": "🔵",
    "esmeralda": "🟢", "ruby": "🟠", "diamante": "🟣", "oficial": "⚫"
}

CARGOS = {
    "bronze": [1502777759863144527, 1502777759863144526],
    "prata": [1502777759880188117, 1502777759863144526],
    "ouro": [1502777759880188118, 1502777759863144526],
    "platina": [1502777759880188119, 1502777759863144526],
    "esmeralda": [1502777759880188120, 1502777759863144526],
    "ruby": [1502777759880188121, 1502777759863144526],
    "diamante": [1502777759880188122, 1502777759863144526],
    "oficial": [1502777759880188123, 1502777759863144526]
}

# ID da Categoria Inicial onde o ticket é aberto antes de ser aceito/definido
# ADICIONE O ID DA SUA CATEGORIA PADRÃO DE TICKETS AQUI:
CATEGORIA_TICKET_INICIAL = 1502777767610155133 

# RegExp para validar as plataformas permitidas
RE_PLATAFORMAS = re.compile(r'(tiktok\.com|instagram\.com|youtube\.com|youtu\.be|kick\.com|facebook\.com)', re.IGNORECASE)

# --- INTERFACES DO USUÁRIO (UI) ---

# Modal de Solicitação
class FormularioSetModal(ui.Modal, title="Solicitação de Set"):
    # 1. Primeiro declaramos apenas os campos de entrada de texto do formulário
    nome_usuario = ui.TextInput(label="Nome Completo", placeholder="Ex: pow-ehrmantraut", min_length=5, max_length=50)
    discord_id = ui.TextInput(label="Identificação (ID)", placeholder="Ex: 37", min_length=1, max_length=300)
    link_plataforma = ui.TextInput(label="Link da Plataforma", placeholder="Ex: twitch.tv/... ou youtube.com/...")
    observacao = ui.TextInput(label="Observação (Opcional)", style=discord.TextStyle.paragraph, required=False, max_length=300)

    # 2. Toda a lógica de processamento e validação acontece obrigatoriamente dentro do on_submit
    async def on_submit(self, interaction: discord.Interaction):
        
        # --- VALIDAÇÃO DO LINK (CORRIGIDO) ---
        # Pegamos o valor digitado no campo 'link_plataforma' usando '.value'
        link_digitado = self.link_plataforma.value
        
        if not RE_PLATAFORMAS.search(link_digitado):
            embed_erro = discord.Embed(
                description="⚠️ Link inválido! Use apenas links de plataformas permitidas (TikTok, Instagram, YouTube, Kick, Facebook).", 
                color=0xFF0000
            )
            # Como ainda não demos defer(), respondemos direto com send_message
            return await interaction.response.send_message(embed=embed_erro, ephemeral=True)

        # Se passou na validação do link, o código continua normalmente:
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        # Criar canal de ticket inicial
        categoria_inicial = guild.get_channel(CATEGORIA_TICKET_INICIAL)
        channel_name = f"🎟️・{self.nome_usuario.value.lower()}"
        
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=categoria_inicial,
            reason=f"Ticket de Set aberto por {interaction.user.name}"
        )
        
        # Setar permissões básicas do ticket
        await ticket_channel.set_permissions(guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        # Montar o Embed com os dados do Modal
        embed = discord.Embed(title="<:emojiJP:1505074670829961236> Contrato Recebido", color=discord.Color.red())
        embed.description = f"Usuário do Discord: {interaction.user.mention}\nUse o menu abaixo para gerenciar esta solicitação."
        embed.add_field(name="Nome Completo:", value=f"`{self.nome_usuario.value}`", inline=True)
        embed.add_field(name="Identificação (ID):", value=f"`{self.discord_id.value}`", inline=True)
        embed.add_field(name="Link da Plataforma:", value=f"{self.link_plataforma.value}", inline=False)
        embed.add_field(name="Observação:", value=f"`{self.observacao.value}`" if self.observacao.value else "`Nenhuma observação informada.`", inline=False)
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif?ex=6a086abd&is=6a07193d&hm=93a51adb8b2d2e5b297285cf62c3cac8f17a1d21743f59b960909cfd5a058ae8&")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1505098549610811462/Criadores_JP_2.png?ex=6a0963c1&is=6a081241&hm=90f76b910373b79f86e88661838d21101075da0480590fb1d7df5a5eaa69fdd1&")
        embed.set_footer(text="Jardim Peri RP - Todos os direitos reservados", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp?ex=6a094d6f&is=6a07fbef&hm=5bd4e53ca8c4b641133b0f855affa243f440b86cdb33410d7579215042d8eba3&")

        # Enviar embed no canal recém-criado junto com o menu de ações administrativo
        await ticket_channel.send(embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario.value))
        
        # --- EMBED E BOTÃO DE REDIRECIONAMENTO ---
        embed_sucesso = discord.Embed(
            title="🎫 Ticket Criado com Sucesso!",
            description=f"Seu formulário foi enviado. Clique no botão abaixo para ir direto ao seu ticket de atendimento.",
            color=discord.Color.red()
        )
        
        view_redirecionamento = ui.View()
        view_redirecionamento.add_item(ui.Button(
            label="Ir para o Ticket", 
            url=ticket_channel.jump_url, 
            style=discord.ButtonStyle.red,
            emoji="<:emojiJP:1505074670829961236>"
        ))
        
        # Como usamos o defer() lá em cima se o link passasse, aqui usamos o followup
        await interaction.followup.send(embed=embed_sucesso, view=view_redirecionamento, ephemeral=True)
        
# Botão Inicial do Canal de Avisos
class BotaoSolicitarSet(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Solicitar Set", style=discord.ButtonStyle.gray, emoji="<:emojiJP:1505074670829961236>", custom_id="btn_solicitar_set")
    async def solicitar_set(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(FormularioSetModal())

# Select Menu com os Níveis (Aceitar / Promover)
class SelectNiveis(ui.Select):
    def __init__(self, nome_usuario, acao):
        self.nome_usuario = nome_usuario
        self.acao = acao # Guarda se a ação atual é "aceitar" ou "promover"
        
        options = [
            discord.SelectOption(label=nivel.capitalize(), value=nivel, emoji=EMOJIS[nivel])
            for nivel in BENEFICIOS.keys()
        ]
        super().__init__(placeholder="⚙️・Gerenciar nível", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            
            nivel = self.values[0]
            guild = interaction.guild
            channel = interaction.channel
            mensagem = interaction.message
            embed = mensagem.embeds[0]

            # --- CAPTURA DE INFORMAÇÕES DO EMBED PARA O APELIDO ---
            nome_modal = self.nome_usuario
            id_modal = ""

            # Varre os campos do embed para resgatar o Nome e ID exatos digitados no modal
            for field in embed.fields:
                if field.name == "Nome Fornecido":
                    nome_modal = field.value
                elif field.name == "ID do Discord":
                    id_modal = field.value

            # --- SISTEMA DE ENTREGA DE CARGOS E ALTERAÇÃO DE APELIDO ---
            import re
            match = re.search(r"<@!?(\d+)>", embed.description)
            
            if match:
                membro_id = int(match.group(1))
                try:
                    membro = guild.get_member(membro_id) or await guild.fetch_member(membro_id)
                except Exception:
                    membro = None
                
                if membro:
                    # 1. Entrega dos Cargos
                    ids_cargos = CARGOS.get(nivel, [])
                    cargos_para_adicionar = [guild.get_role(c_id) for c_id in ids_cargos if guild.get_role(c_id)]
                    
                    if cargos_para_adicionar:
                        try:
                            await membro.add_roles(*cargos_para_adicionar)
                        except discord.Forbidden:
                            print("Bot sem permissão para aplicar os cargos.")

                    # 2. MUDANÇA DE APELIDO (NICKNAME) DO PLAYER
                    novo_apelido = f"{EMOJIS[nivel]} | {nome_modal} - {id_modal}"
                    
                    if len(novo_apelido) > 32:
                        novo_apelido = novo_apelido[:31] + "…"

                    try:
                        await membro.edit(nick=novo_apelido)
                    except discord.Forbidden:
                        print(f"Bot sem permissão para alterar o apelido de {membro.name}.")
                else:
                    print("Dono do ticket não encontrado para receber os cargos/apelido.")

            # --- ATUALIZAÇÃO DO CANAL DO TICKET ---
            # 3. Mantém o canal atualizado também se quiser mover de categoria
            novo_nome_canal = f"{EMOJIS[nivel]}・{nome_modal.lower()}"
            await channel.edit(name=novo_nome_canal)

            id_categoria = CATEGORIAS.get(nivel)
            if id_categoria:
                nova_categoria = guild.get_channel(id_categoria)
                if nova_categoria:
                    await channel.edit(category=nova_categoria)

            # 4. Atualizar o Embed do Canal com os Benefícios
            for i, field in enumerate(embed.fields):
                if field.name.startswith("🎁 Benefícios"):
                    embed.remove_field(i)
                    break

            texto_beneficios = "\n".join(BENEFICIOS[nivel])
            embed.add_field(name=f"🎁 Benefícios - Nível {nivel.capitalize()}", value=texto_beneficios, inline=False)
            embed.color = discord.Color.red()

            # Faz apenas UMA edição limpa apagando o texto de instruções antigo
            await mensagem.edit(content=None, embed=embed, view=MenuGerenciamentoTicket(self.nome_usuario))

            # --- ENVIAR EMBED NA DM DO PLAYER (ACEITO / PROMOVIDO) ---
            if match and membro:
                embed_dm = discord.Embed(
                    title="<:emojiJP:1505074670829961236> Atualização no seu Set de Streamer!",
                    description=f"Olá {membro.mention}, seu set no servidor foi atualizado com sucesso!",
                    color=discord.Color.red()
                )
                embed_dm.add_field(name="Novo Status:", value=f"**`{nivel.capitalize()}` `{EMOJIS[nivel]}`**.", inline=False)
                embed_dm.add_field(name="🎁 Benefícios Liberados:", value=texto_beneficios, inline=False)

                embed_dm.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif?ex=6a086abd&is=6a07193d&hm=93a51adb8b2d2e5b297285cf62c3cac8f17a1d21743f59b960909cfd5a058ae8&")
                embed_dm.set_footer(text="Parabéns e boa sorte com o seu conteúdo!", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp?ex=6a094d6f&is=6a07fbef&hm=5bd4e53ca8c4b641133b0f855affa243f440b86cdb33410d7579215042d8eba3&")
                
                try:
                    await membro.send(embed=embed_dm)
                except discord.Forbidden:
                    print(f"Não foi possível enviar DM para {membro.name} pois a DM dele está fechada.")            


# Select Menu Principal (Aceitar, Recusar, Promover)
class SelectAcoes(ui.Select):
    def __init__(self, nome_usuario=""):
        self.nome_usuario = nome_usuario
        options = [
            discord.SelectOption(label="Aceitar", value="aceitar", description="Aprovar solicitação e escolher nível", emoji="<:AMARELO:1505086398309470288> "),
            discord.SelectOption(label="Recusar", value="recusar", description="Fechar/Recusar o ticket", emoji="<:x1:1505086332936917042>"),
            discord.SelectOption(label="Promover/Rebaixar", value="promover", description="Mudar o nível atual do usuário", emoji="<:ADD:1505086562508214472>")
        ]
        super().__init__(placeholder="⚙️・Painel Administrativo", min_values=1, max_values=1, options=options, custom_id="select_acoes_ticket")


    async def callback(self, interaction: discord.Interaction):
            # --- RESTRICÃO PARA STAFF ---
            CARGO_STAFF_ID = 1502777759880188125
            
            # Verifica se o usuário tem o cargo de Staff
            tem_cargo = any(role.id == CARGO_STAFF_ID for role in interaction.user.roles)
            
            if not tem_cargo:
                        embed_negado = discord.Embed(
                            title="🔒 Acesso Negado",
                            description="Apenas membros da Staff autorizados podem gerenciar este ticket.",
                            color=discord.Color.red()
                        )
                        return await interaction.response.send_message(embed=embed_negado, ephemeral=True)
            
            # Caso tenha o cargo, o fluxo continua normalmente abaixo:
            acao = self.values[0]

            nome_atual = self.nome_usuario
            if not nome_atual:
                if "solicitação-" in interaction.channel.name:
                    nome_atual = interaction.channel.name.split("solicitação-")[-1]
                elif "・" in interaction.channel.name:
                    nome_atual = interaction.channel.name.split("・")[-1]
                else:
                    nome_atual = interaction.channel.name

            if acao in ["aceitar", "promover"]:
                view_niveis = ui.View()
                view_niveis.add_item(SelectNiveis(nome_atual, acao))
                await interaction.response.edit_message(content=f"Selecione o nível para o qual deseja {acao}:", view=view_niveis)
                
# ... (mantenha o início do callback igual, procure por esta condição no final:)
            
            elif acao == "recusar":
                        embed_recusado = discord.Embed(
                            title="❌ Solicitação Recusada",
                            description="Este ticket foi fechado pela administração e o canal será deletado em **5 segundos**.",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=embed_recusado)
                        
                        # --- SISTEMA DE ENVIAR EMBED NA DM DO PLAYER (RECUSADO) ---
                        import re
                        embed_ticket = interaction.message.embeds[0]
                        match_recusa = re.search(r"<@!?(\d+)>", embed_ticket.description)
                        
                        if match_recusa:
                            membro_id = int(match_recusa.group(1))
                            try:
                                membro = guild.get_member(membro_id) or await guild.fetch_member(membro_id)
                                if membro:
                                    embed_dm_recusa = discord.Embed(
                                        title="❌ Atualização no seu Set de Streamer",
                                        description=f"Olá {membro.mention},\n\nSua solicitação de Set de Streamer foi avaliada pela nossa equipe e **não foi aprovada** no momento.",
                                        color=discord.Color.red()
                                    )
                                    embed_dm_recusa.add_field(
                                        name="❓ O que fazer?", 
                                        value="Caso tenha dúvidas sobre os requisitos necessários ou queira tentar novamente no futuro, procure a nossa administração.", 
                                        inline=False
                                    )
                                    embed_dm_recusa.set_footer(text="Agradecemos o seu interesse!")
                                    
                                    await membro.send(embed=embed_dm_recusa)
                            except Exception:
                                print("Não foi possível notificar o usuário da recusa via DM.")

                        # Prossegue com a exclusão do ticket normalmente
                        await interaction.message.delete()
                        import asyncio
                        await asyncio.sleep(5)
                        await interaction.channel.delete()


class MenuGerenciamentoTicket(ui.View):
    def __init__(self, nome_usuario=""):
        # timeout=None é obrigatório para persistência
        super().__init__(timeout=None)
        self.add_item(SelectAcoes(nome_usuario))


# --- COMANDOS E EVENTOS DE INICIALIZAÇÃO ---

@bot.event
async def on_ready():
    print(f"Bot logado com sucesso como {bot.user}")
    
    # Registra a view do botão principal do painel
    bot.add_view(BotaoSolicitarSet())
    
    # Registra a view do menu de gerenciamento dos tickets para que funcione após reiniciar
    bot.add_view(MenuGerenciamentoTicket())
    
    print("📌 Todas as Views Persistentes foram carregadas com sucesso!")

@bot.command()
@commands.has_permissions(administrator=True)
async def JP1(ctx):  # <--- Corrigido aqui!
    """Comando para enviar o painel com o botão de Solicitar Set"""
    embed = discord.Embed(
        title="<:emojiJP:1505074670829961236> Jardim Peri - Solicitação de Contrato",
        description="> Seja bem-vindo ao painel de solicitação de contrato! Para solicitar um set.\n\n" "> clique no botão abaixo e preencha o formulário com suas informações.\n\n" "> Nossa equipe irá analisar sua solicitação e entrar em contato o mais breve possível.\n\n" "> Obrigado por escolher o Jardim Peri!\n\n"
        "**Tenha em mãos as seguintes informações para agilizar sua solicitação:**\n\n"
        "🔸`Nome Completo`\n"
        "🔸`Identificação (ID)`\n"
        "🔸`Link da Plataforma`\n"
        "🔸`Observação (Opcional)`\n",
        color=discord.Color.red()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1444735189765849320/1503019230910746654/GIF_PERI.gif?ex=6a086abd&is=6a07193d&hm=93a51adb8b2d2e5b297285cf62c3cac8f17a1d21743f59b960909cfd5a058ae8&")

    embed.set_image(url="https://cdn.discordapp.com/attachments/1444735189765849320/1505098549610811462/Criadores_JP_2.png?ex=6a0963c1&is=6a081241&hm=90f76b910373b79f86e88661838d21101075da0480590fb1d7df5a5eaa69fdd1&")

    embed.set_footer(text="Jardim Peri RP - Todos os direitos reservados", icon_url="https://cdn.discordapp.com/attachments/1444735189765849320/1505074583601025114/emoji_JP.webp?ex=6a094d6f&is=6a07fbef&hm=5bd4e53ca8c4b641133b0f855affa243f440b86cdb33410d7579215042d8eba3&")
    await ctx.send(embed=embed, view=BotaoSolicitarSet())

# Insira o Token do seu Bot do Discord abaixo
bot.run(TOKEN)