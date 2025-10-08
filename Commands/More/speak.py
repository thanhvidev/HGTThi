import asyncio
import os
import discord
from discord.ext import commands
import azure.cognitiveservices.speech as speechsdk

voice_dict = {
    "nu": "vi-VN-HoaiMyNeural",  # Giọng nói mặc định
    "nam": "vi-VN-NamMinhNeural",  # Giọng nói nam
}

class Speak(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.current_voice = "nam"

    @commands.command(name="speak", aliases=["s", "sp"], description="Nói liên tục luôn")
    async def speak(self, ctx, *args):
        text = " ".join(args)
        if not text:
            await ctx.send("Hãy nhập nội dung bạn muốn nói!")
            return

        user = ctx.author
        if not user.voice:
            await ctx.send("Vui lòng vào kênh thoại trước!")
            return

        vc = ctx.voice_client
        if not vc:
            try:
                vc = await user.voice.channel.connect()
            except Exception as e:
                await ctx.send(f"Không thể kết nối vào kênh: {e}")
                return
        elif vc.channel != user.voice.channel:
            await ctx.send("Bạn phải ở chung kênh với tôi mới nói chuyện được!")
            return
        voice_name = self.current_voice  
        voice = voice_dict.get(voice_name, voice_dict["nam"])

        # Sử dụng Azure Cognitive Services để chuyển văn bản thành giọng nói
        speech_config = speechsdk.SpeechConfig(subscription="471b65ebc8ab4ea49a31d9dfa79633a9", region="eastasia")
        speech_config.speech_synthesis_voice_name = voice

        file_name = "tts.mp3"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            if vc.is_playing():
                vc.stop()

            # Sử dụng FFmpeg để phát tệp âm thanh
            source = discord.FFmpegPCMAudio(file_name, executable="ffmpeg")
            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

            os.remove(file_name)
        else:
            await ctx.send("Có lỗi xảy ra khi chuyển văn bản thành giọng nói.")

    @speak.error
    async def speak_error(self, ctx, error):
        await ctx.send("Có lỗi xảy ra khi nói chuyện")
    
    @commands.command(name="voice", aliases=["sv"], description="Đổi giọng nói")
    async def voice(self, ctx, voice_name=None):  
        if voice_name is None:  
            await ctx.send("Chọn giọng nói sử dụng lệnh `zsv [nam hoặc nu]`")  
            return  

        if voice_name in voice_dict:  
            self.current_voice = voice_name  
            await ctx.send(f"Giọng nói đã được thay đổi thành: {voice_name}")  
        else:  
            await ctx.send(f"Giọng nói '{voice_name}' không tồn tại!")  


    @commands.command(name="dis", description="Rời khỏi kênh")
    async def dis(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
        else:
            await ctx.send("Tôi không ở trong kênh nào cả")

    @dis.error
    async def leave_error(self, ctx, error):
        await ctx.send("Có lỗi xảy ra khi rời khỏi kênh")

async def setup(client):
    await client.add_cog(Speak(client))