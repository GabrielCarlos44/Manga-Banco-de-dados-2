"""
Aplicação CLI - Sistema de Gerenciamento de Mangás
Demonstra CRUD completo usando SQLAlchemy ORM
"""

import os
from datetime import datetime
from database import get_session
from models import (
    Manga, Capitulo, Genero, MangaGenero,
    Usuario, Leitor, Administrador,
    Avaliacao, Comentario, LeitorManga,
    Status
)
from sqlalchemy import func, desc


class MangaApp:
    def __init__(self):
        self.session = get_session()
        self.usuario_logado = None
    
    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pausar(self):
        input("\nPressione ENTER para continuar...")
    
    def menu_principal(self):
        while True:
            self.limpar_tela()
            print("=" * 60)
            print("     SISTEMA DE GERENCIAMENTO DE MANGÁS")
            print("=" * 60)
            
            if self.usuario_logado:
                tipo = "ADMIN" if isinstance(self.usuario_logado, Administrador) else "LEITOR"
                print(f"\n👤 Logado como: {self.usuario_logado.nome} ({tipo})")
            
            print("\n1. Gerenciar Mangás")
            print("2. Gerenciar Capítulos")
            print("3. Gerenciar Gêneros")
            print("4. Gerenciar Leitores")
            print("5. Gerenciar Avaliações")
            print("6. Gerenciar Comentários")
            print("7. Relatórios e Estatísticas")
            print("8. Login/Logout")
            print("0. Sair")
            
            escolha = input("\nEscolha uma opção: ")
            
            if escolha == "1":
                self.menu_mangas()
            elif escolha == "2":
                self.menu_capitulos()
            elif escolha == "3":
                self.menu_generos()
            elif escolha == "4":
                self.menu_leitores()
            elif escolha == "5":
                self.menu_avaliacoes()
            elif escolha == "6":
                self.menu_comentarios()
            elif escolha == "7":
                self.menu_relatorios()
            elif escolha == "8":
                self.menu_auth()
            elif escolha == "0":
                print("\n👋 Até logo!")
                self.session.close()
                break
    
    # ==================== CRUD MANGÁS ====================
    
    def menu_mangas(self):
        while True:
            self.limpar_tela()
            print("=" * 60)
            print("     GERENCIAR MANGÁS")
            print("=" * 60)
            print("\n1. Listar Mangás")
            print("2. Criar Mangá")
            print("3. Atualizar Mangá")
            print("4. Excluir Mangá")
            print("5. Ver Detalhes do Mangá")
            print("0. Voltar")
            
            escolha = input("\nEscolha uma opção: ")
            
            if escolha == "1":
                self.listar_mangas()
            elif escolha == "2":
                self.criar_manga()
            elif escolha == "3":
                self.atualizar_manga()
            elif escolha == "4":
                self.excluir_manga()
            elif escolha == "5":
                self.ver_detalhes_manga()
            elif escolha == "0":
                break
    
    def listar_mangas(self):
        print("\n LISTA DE MANGÁS\n")
        print("-" * 80)
        
        mangas = self.session.query(Manga).all()
        
        if not mangas:
            print("Nenhum mangá cadastrado.")
        else:
            print(f"{'ID':<5} {'Título':<30} {'Autor':<20} {'Status':<15}")
            print("-" * 80)
            for manga in mangas:
                print(f"{manga.id_manga:<5} {manga.titulo_manga:<30} {manga.autor:<20} {manga.status.value:<15}")
        
        print(f"\nTotal: {len(mangas)} mangás")
        self.pausar()
    
    def criar_manga(self):
        print("\n CRIAR NOVO MANGÁ\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print("❌ Apenas administradores podem criar mangás!")
            self.pausar()
            return
        
        try:
            titulo = input("Título: ")
            autor = input("Autor: ")
            
            print("\nStatus:")
            print("1. Em Andamento")
            print("2. Concluído")
            print("3. Pausado")
            status_escolha = input("Escolha: ")
            
            status_map = {
                "1": Status.EM_ANDAMENTO,
                "2": Status.CONCLUIDO,
                "3": Status.HIATO
            }
            status = status_map.get(status_escolha, Status.EM_ANDAMENTO)
            
            # Criar mangá
            manga = Manga(
                titulo_manga=titulo,
                autor=autor,
                status=status
            )
            self.session.add(manga)
            self.session.flush()  # Para obter o ID
            
            # Adicionar gêneros
            print("\nGêneros disponíveis:")
            generos = self.session.query(Genero).all()
            for i, g in enumerate(generos, 1):
                print(f"{i}. {g.tipo_genero}")
            
            generos_escolhidos = input("\nEscolha os gêneros (separados por vírgula): ").split(",")
            principal_idx = input("Qual é o principal? (número): ")
            
            for idx in generos_escolhidos:
                idx = idx.strip()
                if idx.isdigit() and 1 <= int(idx) <= len(generos):
                    genero = generos[int(idx) - 1]
                    manga_genero = MangaGenero(
                        id_manga=manga.id_manga,
                        id_genero=genero.id_genero,
                        principal=(idx == principal_idx)
                    )
                    self.session.add(manga_genero)
            
            # Incrementar contador do admin
            self.usuario_logado.numero_de_mangas_upados += 1
            
            self.session.commit()
            
            print(f"\n✅ Mangá '{titulo}' criado com sucesso! (ID: {manga.id_manga})")
            
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro ao criar mangá: {e}")
        
        self.pausar()
    
    def atualizar_manga(self):
        print("\n ATUALIZAR MANGÁ\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem atualizar mangás!")
            self.pausar()
            return
        
        try:
            manga_id = int(input("ID do mangá: "))
            manga = self.session.query(Manga).get(manga_id)
            
            if not manga:
                print(" Mangá não encontrado!")
                self.pausar()
                return
            
            print(f"\nMangá atual: {manga.titulo_manga}")
            print(f"Autor: {manga.autor}")
            print(f"Status: {manga.status.value}")
            
            novo_titulo = input(f"\nNovo título (Enter para manter '{manga.titulo_manga}'): ")
            novo_autor = input(f"Novo autor (Enter para manter '{manga.autor}'): ")
            
            if novo_titulo:
                manga.titulo_manga = novo_titulo
            if novo_autor:
                manga.autor = novo_autor
            
            print("\nNovo status:")
            print("1. Em Andamento")
            print("2. Concluído")
            print("3. Pausado")
            print("4. Manter atual")
            
            status_escolha = input("Escolha: ")
            if status_escolha == "1":
                manga.status = Status.EM_ANDAMENTO
            elif status_escolha == "2":
                manga.status = Status.CONCLUIDO
            elif status_escolha == "3":
                manga.status = Status.PAUSADO
            
            self.session.commit()
            print(f"\n Mangá atualizado com sucesso!")
            
        except ValueError:
            print("❌ ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n❌ Erro ao atualizar mangá: {e}")
        
        self.pausar()
    
    def excluir_manga(self):
        print("\n EXCLUIR MANGÁ\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem excluir mangás!")
            self.pausar()
            return
        
        try:
            manga_id = int(input("ID do mangá: "))
            manga = self.session.query(Manga).get(manga_id)
            
            if not manga:
                print(" Mangá não encontrado!")
                self.pausar()
                return
            
            print(f"\nTem certeza que deseja excluir '{manga.titulo_manga}'?")
            confirmacao = input("Digite 'SIM' para confirmar: ")
            
            if confirmacao.upper() == "SIM":
                self.session.delete(manga)
                self.session.commit()
                print(f"\n Mangá excluído com sucesso!")
            else:
                print("\n Operação cancelada.")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro ao excluir mangá: {e}")
        
        self.pausar()
    
    def ver_detalhes_manga(self):
        print("\n DETALHES DO MANGÁ\n")
        
        try:
            manga_id = int(input("ID do mangá: "))
            manga = self.session.query(Manga).get(manga_id)
            
            if not manga:
                print("❌ Mangá não encontrado!")
                self.pausar()
                return
            
            print("\n" + "=" * 60)
            print(f" {manga.titulo_manga}")
            print("=" * 60)
            print(f"Autor: {manga.autor}")
            print(f"Status: {manga.status.value}")
            print(f"Data de Criação: {manga.data_criacao.strftime('%d/%m/%Y %H:%M')}")
            
            # Gêneros
            generos = [f"{mg.genero.tipo_genero}" + (" ⭐Principal" if mg.principal else "") 
                      for mg in manga.manga_generos]
            print(f"Gêneros: {', '.join(generos) if generos else 'Nenhum'}")
            
            # Capítulos
            print(f"\n Capítulos: {len(manga.capitulos)}")
            for cap in manga.capitulos:
                print(f"   {cap.numero_capitulo}. {cap.titulo_capitulo} ({cap.numero_paginas} páginas)")
            
            # Avaliações
            if manga.avaliacoes:
                media = sum(av.nota for av in manga.avaliacoes) / len(manga.avaliacoes)
                print(f"\n Avaliações: {len(manga.avaliacoes)} (Média: {media:.2f})")
            else:
                print("\n Sem avaliações")
            
            # Comentários
            print(f"\n Comentários: {len(manga.comentarios)}")
            for com in manga.comentarios[:3]:
                print(f"   - {com.leitor.codinome}: {com.texto_comentario[:50]}...")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    # ==================== CRUD CAPÍTULOS ====================
    
    def menu_capitulos(self):
        while True:
            self.limpar_tela()
            print("=" * 60)
            print("     GERENCIAR CAPÍTULOS")
            print("=" * 60)
            print("\n1. Listar Capítulos de um Mangá")
            print("2. Criar Capítulo")
            print("3. Marcar como Lido")
            print("4. Excluir Capítulo")
            print("0. Voltar")
            
            escolha = input("\nEscolha uma opção: ")
            
            if escolha == "1":
                self.listar_capitulos()
            elif escolha == "2":
                self.criar_capitulo()
            elif escolha == "3":
                self.marcar_lido()
            elif escolha == "4":
                self.excluir_capitulo()
            elif escolha == "0":
                break
    
    def listar_capitulos(self):
        print("\n LISTAR CAPÍTULOS\n")
        
        try:
            manga_id = int(input("ID do mangá: "))
            manga = self.session.query(Manga).get(manga_id)
            
            if not manga:
                print("❌ Mangá não encontrado!")
                self.pausar()
                return
            
            print(f"\nCapítulos de '{manga.titulo_manga}':\n")
            print(f"{'Nº':<5} {'Título':<40} {'Páginas':<10} {'Lidas':<10}")
            print("-" * 70)
            
            for cap in manga.capitulos:
                print(f"{cap.numero_capitulo:<5} {cap.titulo_capitulo:<40} {cap.numero_paginas:<10} {cap.paginas_lidas:<10}")
            
            print(f"\nTotal: {len(manga.capitulos)} capítulos")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            print(f" Erro: {e}")
        
        self.pausar()
    
    def criar_capitulo(self):
        print("\n CRIAR CAPÍTULO\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem criar capítulos!")
            self.pausar()
            return
        
        try:
            manga_id = int(input("ID do mangá: "))
            manga = self.session.query(Manga).get(manga_id)
            
            if not manga:
                print(" Mangá não encontrado!")
                self.pausar()
                return
            
            titulo = input("Título do capítulo: ")
            numero = int(input("Número do capítulo: "))
            paginas = int(input("Número de páginas: "))
            
            capitulo = Capitulo(
                titulo_capitulo=titulo,
                numero_capitulo=numero,
                numero_paginas=paginas,
                id_manga=manga_id
            )
            
            self.session.add(capitulo)
            self.session.commit()
            
            print(f"\n Capítulo '{titulo}' criado com sucesso!")
            
        except ValueError:
            print(" Valores inválidos!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    def marcar_lido(self):
        print("\n✓ MARCAR CAPÍTULO COMO LIDO\n")
        
        if not isinstance(self.usuario_logado, Leitor):
            print(" Apenas leitores podem marcar capítulos como lidos!")
            self.pausar()
            return
        
        try:
            cap_id = int(input("ID do capítulo: "))
            capitulo = self.session.query(Capitulo).get(cap_id)
            
            if not capitulo:
                print(" Capítulo não encontrado!")
                self.pausar()
                return
            
            # Usar o método concluir()
            capitulo.concluir()
            
            # Atualizar progresso do leitor
            leitor_manga = self.session.query(LeitorManga).filter_by(
                id_leitor=self.usuario_logado.id_usuario,
                id_manga=capitulo.id_manga
            ).first()
            
            if not leitor_manga:
                # Criar registro se não existir
                leitor_manga = LeitorManga(
                    id_leitor=self.usuario_logado.id_usuario,
                    id_manga=capitulo.id_manga
                )
                self.session.add(leitor_manga)
            
            # Calcular progresso
            total_caps = len(capitulo.manga.capitulos)
            leitor_manga.ultimo_capitulo_lido = capitulo.numero_capitulo
            leitor_manga.progresso_leitura = (capitulo.numero_capitulo / total_caps) * 100
            
            self.session.commit()
            
            print(f"\n Capítulo marcado como lido!")
            print(f"Progresso em '{capitulo.manga.titulo_manga}': {leitor_manga.progresso_leitura:.1f}%")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    def excluir_capitulo(self):
        print("\n EXCLUIR CAPÍTULO\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem excluir capítulos!")
            self.pausar()
            return
        
        try:
            cap_id = int(input("ID do capítulo: "))
            capitulo = self.session.query(Capitulo).get(cap_id)
            
            if not capitulo:
                print(" Capítulo não encontrado!")
                self.pausar()
                return
            
            confirmacao = input(f"Excluir '{capitulo.titulo_capitulo}'? (SIM/não): ")
            
            if confirmacao.upper() == "SIM":
                self.session.delete(capitulo)
                self.session.commit()
                print("\n Capítulo excluído!")
            else:
                print("\n Cancelado.")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    # ==================== CRUD GÊNEROS ====================
    
    def menu_generos(self):
        while True:
            self.limpar_tela()
            print("=" * 60)
            print("     GERENCIAR GÊNEROS")
            print("=" * 60)
            print("\n1. Listar Gêneros")
            print("2. Criar Gênero")
            print("3. Renomear Gênero")
            print("4. Excluir Gênero")
            print("0. Voltar")
            
            escolha = input("\nEscolha uma opção: ")
            
            if escolha == "1":
                self.listar_generos()
            elif escolha == "2":
                self.criar_genero()
            elif escolha == "3":
                self.renomear_genero()
            elif escolha == "4":
                self.excluir_genero()
            elif escolha == "0":
                break
    
    def listar_generos(self):
        print("\n LISTA DE GÊNEROS\n")
        
        generos = self.session.query(
            Genero,
            func.count(MangaGenero.id_manga).label('total_mangas')
        ).outerjoin(MangaGenero).group_by(Genero.id_genero).all()
        
        print(f"{'ID':<5} {'Gênero':<25} {'Total Mangás':<15}")
        print("-" * 50)
        
        for genero, total in generos:
            print(f"{genero.id_genero:<5} {genero.tipo_genero:<25} {total:<15}")
        
        print(f"\nTotal: {len(generos)} gêneros")
        self.pausar()
    
    def criar_genero(self):
        print("\n CRIAR GÊNERO\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem criar gêneros!")
            self.pausar()
            return
        
        try:
            nome = input("Nome do gênero: ")
            
            genero = Genero(tipo_genero=nome)
            self.session.add(genero)
            self.session.commit()
            
            print(f"\n Gênero '{nome}' criado com sucesso!")
            
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    def renomear_genero(self):
        print("\n RENOMEAR GÊNERO\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem renomear gêneros!")
            self.pausar()
            return
        
        try:
            genero_id = int(input("ID do gênero: "))
            genero = self.session.query(Genero).get(genero_id)
            
            if not genero:
                print(" Gênero não encontrado!")
                self.pausar()
                return
            
            print(f"Gênero atual: {genero.tipo_genero}")
            novo_nome = input("Novo nome: ")
            
            genero.renomear(novo_nome)
            self.session.commit()
            
            print(f"\n Gênero renomeado para '{novo_nome}'!")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    def excluir_genero(self):
        print("\n EXCLUIR GÊNERO\n")
        
        if not isinstance(self.usuario_logado, Administrador):
            print(" Apenas administradores podem excluir gêneros!")
            self.pausar()
            return
        
        try:
            genero_id = int(input("ID do gênero: "))
            genero = self.session.query(Genero).get(genero_id)
            
            if not genero:
                print(" Gênero não encontrado!")
                self.pausar()
                return
            
            # Verificar se há mangás usando este gênero
            total = self.session.query(MangaGenero).filter_by(id_genero=genero_id).count()
            
            if total > 0:
                print(f"  Este gênero está sendo usado por {total} mangá(s)!")
                confirmacao = input("Continuar mesmo assim? (SIM/não): ")
                if confirmacao.upper() != "SIM":
                    print("\n Cancelado.")
                    self.pausar()
                    return
            
            self.session.delete(genero)
            self.session.commit()
            
            print(f"\n Gênero excluído!")
            
        except ValueError:
            print(" ID inválido!")
        except Exception as e:
            self.session.rollback()
            print(f"\n Erro: {e}")
        
        self.pausar()
    
    # ==================== OUTROS MENUS (simplificados) ====================
    
    def menu_leitores(self):
        print("\n Funcionalidade em construção...")
        self.pausar()
    
    def menu_avaliacoes(self):
        print("\n Funcionalidade em construção...")
        self.pausar()
    
    def menu_comentarios(self):
        print("\n Funcionalidade em construção...")
        self.pausar()
    
    def menu_relatorios(self):
        print("\n Funcionalidade em construção...")
        self.pausar()
    
    def menu_auth(self):
        if self.usuario_logado:
            self.usuario_logado = None
            print("\n Logout realizado!")
        else:
            print("\n LOGIN\n")
            email = input("Email: ")
            senha = input("Senha: ")
            
            usuario = self.session.query(Usuario).filter_by(email=email).first()
            
            if usuario and usuario.verificar_senha(senha):
                self.usuario_logado = usuario
                print(f"\n Bem-vindo, {usuario.nome}!")
            else:
                print("\n Credenciais inválidas!")
        
        self.pausar()


if __name__ == "__main__":
    app = MangaApp()
    app.menu_principal()
