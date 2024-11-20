import discord
from discord.py import app_commands
from discord.ext import commands

from youtube_dl import YoutubeDL


class MeuGitHub(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.timeout=399

        github = discord.ui.Button(label="Desenvolvido por Paulo Alarico",url="https://www.github.com")
        self.add_item(github)

class config_musica(commands.Cog):   
    def __init__(self, client):
        self.client = client
        self.tocando = False
        
        self.fila_musica = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'} #Config de definição da LIB do YouTube.
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = ""


    def busca(self, procura):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % procura, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def pular_musica(self):
        if len(self.fila_musica) > 0:
            self.tocando = True

           
            url_musica = self.fila_musica[0][0]['source'] #url da musica que está tocando atualmente
            self.fila_musica.pop(0) #Define como 0, para de tocar a musica atual.
            self.vc.play(discord.FFmpegPCMAudio(url_musica, **self.FFMPEG_OPTIONS), after=lambda e: self.proxima_musica())
        else:
            self.tocando = False

    # loop para tocar a musica
    async def tocar_musica(self):
        if len(self.fila_musica) > 0:
            self.tocando = True

            url_musica = self.fila_musica[0][0]['source']
            
            
            # tentativa de conectar em um canal (o bot só conecta quando o usuário o ativa estando conectado a uma chamada)
            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.fila_musica[0][1].connect()
            else:
                await self.vc.move_to(self.fila_musica[0][1])
            
            print(self.fila_musica)
            self.fila_musica.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(url_musica, **self.FFMPEG_OPTIONS), after=lambda e: self.proxima_musica())
        else:
            self.tocando = False
            await self.vc.disconnect()
   
    
   
    
   
    #AQUI COMEÇO A SETAR OS COMANDOS DO BOT
    


    @app_commands.command(name="TOCAR",message="Reproduz uma música")
    @app_commands.describe(
        busca = "Coloque aqui o nome da sua música: "
    )
    async def play(self, interaction:discord.Interaction,busca:str):
        await interaction.response.defer(thinking=True)
        query = busca
        
        #Aqui ele puxa conforme o canal do usuário
        try:
            canal_conectado = interaction.user.voice.channel
        except:
            embedvc = discord.Embed(
                cor_mensagem = 12255232, #vermelho
                mensagem = 'Você deve estar conectado a um canal de voz para reproduzir alguma música. '
            )
            await interaction.followup.send(embed=embedvc)
            return
        else:
            tocar_musica = self.busca(query)
            if type(tocar_musica) == type(True):
                embedvc = discord.Embed(
                    cor_mensagem = 12255232,#vermelho
                    mensagem = 'Não consegui colocar a sua música, tente novamente. '
                )
                await interaction.followup.send(embed=embedvc)
            else:
                embedvc = discord.Embed(
                    cor_mensagem = 32768,#green
                    mensagem = f"Você adicionou a música **{tocar_musica['title']}** à fila!"
                )
                await interaction.followup.send(embed=embedvc,view=MeuGitHub())
                self.fila_musica.append([tocar_musica, canal_conectado])
                
                if self.tocando == False:
                    await self.tocar_musica()

    @app_commands.command(name="fila",message="Mostra as atuais músicas da fila.")
    async def q(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        retval = ""
        for i in range(0, len(self.fila_musica)):
            retval += f'**{i+1} - **' + self.fila_musica[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            embedvc = discord.Embed(
                cor_mensagem= 12255232,
                mensagem = f"{retval}"
            )
            await interaction.followup.send(embed=embedvc)
        else:
            embedvc = discord.Embed(
                cor_mensagem= 1646116,
                mensagem = 'Não existe músicas na fila no momento.'
            )
            await interaction.followup.send(embed=embedvc)

    @app_commands.command(name="pular",message="Pula a atual música que está tocando.")
    @app_commands.default_permissions(manage_channels=True)
    async def pular(self, interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        if self.vc != "" and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.tocar_musica()
            embedvc = discord.Embed(
                cor_mensagem= 1646116,#verde
                mensagem = "Você pulou a música."
            )
            await interaction.followup.send(embed=embedvc)
    
    @app_commands.command(name="SOBRE",message="Tudo sobre o BOT")
    async def help(self,interaction:discord.Interaction):
        await interaction.response.defer(thinking=True)
        ajudame = "`/ajuda` - Veja esse guia!\n`/play` - Toque uma música do YouTube!\n`/fila` - Veja a fila de músicas na Playlist\n`/pular` - Pule para a próxima música da fila"
        comando_ajuda = discord.Embed(
            cor_mensagem = 1646116,#verde
            title=f'Comandos do {self.client.user.name}', #Pega o nome do usuario e retorna a ajuda
            mensagem = ajudame
        )
        try:
            comando_ajuda.set_thumbnail(url=self.client.user.avatar.url)
        except:
            pass
        await interaction.followup.send(embed=comando_ajuda,view=MeuGitHub())

    @pular.error #Erros para kick
    async def pular_erro(self,interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, commands.MissingPermissions):
            embedvc = discord.Embed(
                cor_mensagem= 12255232, #vermel
                mensagem = "BOT sem permissão de Gerenciar canais para pular músicas."
            )
            await interaction.followup.send(embed=embedvc)     
        else:
            raise error

async def setup(client):
    await client.add_cog(config_musica(client))
    
