import hashlib
import time
from multiprocessing import Pool

def worker_velocidade_maxima(args):
    """
    Worker altamente otimizado que trabalha puramente com bytes.
    """
    inicio, fim, target_digest = args
    
    for i in range(inicio, fim):
        # OTIMIZAÇÃO 1: Formatação direta em bytes (pula a criação de strings e encode)
        combinacao_bytes = b"%09d" % i
        
        # OTIMIZAÇÃO 2: Comparação usando .digest() puro, muito mais rápido que .hexdigest()
        if hashlib.md5(combinacao_bytes).digest() == target_digest:
            return combinacao_bytes.decode('utf-8')
            
    return None

def quebrar_hash_turbo(hash_hex, digitos=9, num_workers=1):
    total_combinacoes = 10 ** digitos
    
    # Prepara o alvo já no formato de bytes puros para otimizar a comparação
    target_digest = bytes.fromhex(hash_hex)
    
    print(f"\nIniciando teste com {num_workers} worker(s)...")
    inicio_tempo = time.time()
    
    resultado_final = None
    
    if num_workers == 1:
        # Modo Serial puro
        resultado_final = worker_velocidade_maxima((0, total_combinacoes, target_digest))
    else:
        # Modo Paralelo
        tamanho_lote = total_combinacoes // num_workers
        lotes = []
        for i in range(num_workers):
            inicio = i * tamanho_lote
            fim = (i + 1) * tamanho_lote if i != (num_workers - 1) else total_combinacoes
            lotes.append((inicio, fim, target_digest))
            
        with Pool(processes=num_workers) as pool:
            # imap_unordered é mais rápido e permite parar assim que achar
            for resultado in pool.imap_unordered(worker_velocidade_maxima, lotes):
                if resultado is not None:
                    resultado_final = resultado
                    pool.terminate() # OTIMIZAÇÃO 3: Interrompe os outros workers imediatamente
                    break
                    
    tempo_execucao = time.time() - inicio_tempo
    
    if resultado_final:
        print(f"-> SUCESSO! Senha: {resultado_final}")
    else:
        print("-> Senha não encontrada no espaço de busca.")
        
    print(f"-> Tempo registrado: {tempo_execucao:.4f} segundos")
    return tempo_execucao

if __name__ == '__main__':
    # O hash alvo do seu exercício
    HASH_ALVO = "ca6ae33116b93e57b87810a27296fc36"
    
    print("="*50)
    print("  INICIANDO BENCHMARK - QUEBRA DE MD5 (9 DÍGITOS)  ")
    print("="*50)
    
    tempos = {}
    cenarios = [1, 2, 4, 8, 12]
    
    for workers in cenarios:
        tempos[workers] = quebrar_hash_turbo(HASH_ALVO, num_workers=workers)
        
    print("\n" + "="*50)
    print(" RESULTADOS FINAIS PARA A SUA PLANILHA EXCEL ")
    print("="*50)
    print("Workers | Tempo (s) | Speedup | Eficiência (%)")
    print("-" * 46)
    
    tempo_base = tempos[1]
    for w in cenarios:
        t = tempos[w]
        speedup = tempo_base / t
        eficiencia = (speedup / w) * 100
        print(f"{w:^7} | {t:^9.2f} | {speedup:^7.2f} | {eficiencia:^13.1f}%")