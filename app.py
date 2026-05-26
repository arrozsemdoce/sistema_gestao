from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Usuario, Produto, Cliente, Lead
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def dashboard():
    total_produtos = Produto.query.count()
    total_clientes = Cliente.query.count()
    total_leads = Lead.query.count()
    return render_template('dashboard.html', total_produtos=total_produtos, total_clientes=total_clientes, total_leads=total_leads)

# AUTH
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = Usuario.query.filter_by(email=request.form['email']).first()
        if usuario and check_password_hash(usuario.senha, request.form['senha']):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect(url_for('dashboard'))
        flash('Email ou senha inválidos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ESTOQUE
@app.route('/estoque')
@login_required
def estoque():
    produtos = Produto.query.all()
    return render_template('estoque.html', produtos=produtos)

@app.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    if request.method == 'POST':
        produto = Produto(
            nome=request.form['nome'],
            codigo=request.form['codigo'],
            quantidade=int(request.form['quantidade']),
            preco=float(request.form['preco'])
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('estoque'))
    return render_template('produto_form.html')

@app.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.codigo = request.form['codigo']
        produto.quantidade = int(request.form['quantidade'])
        produto.preco = float(request.form['preco'])
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('estoque'))
    return render_template('produto_form.html', produto=produto)

@app.route('/estoque/deletar/<int:id>')
@login_required
def deletar_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto removido!', 'warning')
    return redirect(url_for('estoque'))

# CLIENTES
@app.route('/clientes')
@login_required
def clientes():
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        cliente = Cliente(
            nome=request.form['nome'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            endereco=request.form['endereco']
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html')

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.email = request.form['email']
        cliente.telefone = request.form['telefone']
        cliente.endereco = request.form['endereco']
        db.session.commit()
        flash('Cliente atualizado!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/deletar/<int:id>')
@login_required
def deletar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente removido!', 'warning')
    return redirect(url_for('clientes'))

# CRM
@app.route('/crm')
@login_required
def crm():
    leads = Lead.query.all()
    return render_template('crm.html', leads=leads)

@app.route('/crm/novo', methods=['GET', 'POST'])
@login_required
def novo_lead():
    if request.method == 'POST':
        lead = Lead(
            titulo=request.form['titulo'],
            cliente=request.form['cliente'],
            valor=float(request.form['valor'] or 0),
            status=request.form['status']
        )
        db.session.add(lead)
        db.session.commit()
        flash('Lead cadastrado com sucesso!', 'success')
        return redirect(url_for('crm'))
    return render_template('lead_form.html')

@app.route('/crm/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'POST':
        lead.titulo = request.form['titulo']
        lead.cliente = request.form['cliente']
        lead.valor = float(request.form['valor'] or 0)
        lead.status = request.form['status']
        db.session.commit()
        flash('Lead atualizado!', 'success')
        return redirect(url_for('crm'))
    return render_template('lead_form.html', lead=lead)

@app.route('/crm/deletar/<int:id>')
@login_required
def deletar_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    flash('Lead removido!', 'warning')
    return redirect(url_for('crm'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Usuario.query.first():
            admin = Usuario(nome='Admin', email='admin@admin.com', senha=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
