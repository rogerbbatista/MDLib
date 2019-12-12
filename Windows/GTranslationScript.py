import vlibras_translate
import sys

endLine = "#_#"
tradutor = vlibras_translate.translation.Translation()
entrada = open(sys.argv[1] + "/tempTeste.txt")
lines = entrada.read()
lines = lines.splitlines()
translation = ""
for line in lines:
    translation += tradutor.rule_translation(line)
    translation += endLine
    
arquivoSaida = open(sys.argv[1] + "/outputTranslation.txt", "wb+")
arquivoSaida.write(translation.encode('utf-8'))
