
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(subject, recipient, html_content):
    """
    Send an email notification
    """
    if not settings.EMAIL_ENABLED:
        logger.warning(f"Email sending is disabled. Would have sent to {recipient}: {subject}")
        return False
    
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = recipient
        
        # Create the HTML part of the message
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        if settings.SMTP_USE_TLS:
            server.starttls()
        
        # Login if credentials are provided
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # Send email
        server.sendmail(settings.EMAIL_SENDER, recipient, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        return False

def send_quote_notification(quote_data):
    """
    Send an email notification for a new quote request
    """
    recipient = "cscheidegger@gmail.com"  # Fixed recipient as requested
    subject = f"Novo Orçamento Solicitado - #{quote_data['id']}"
    
    # Create HTML content for the email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4f46e5; color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9fafb; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280; }}
            .button {{ display: inline-block; background-color: #4f46e5; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Novo Orçamento Solicitado</h2>
            </div>
            <div class="content">
                <p>Olá,</p>
                <p>Um novo pedido de orçamento foi submetido com os seguintes detalhes:</p>
                <ul>
                    <li><strong>ID do Orçamento:</strong> #{quote_data['id']}</li>
                    <li><strong>Descrição:</strong> {quote_data['description']}</li>
                    <li><strong>Status:</strong> {quote_data['status']}</li>
                    <li><strong>Data:</strong> {quote_data['created_at']}</li>
                </ul>
                <p>Você pode visualizar e gerenciar este orçamento no painel administrativo.</p>
                <a href="{settings.FRONTEND_URL}/admin/quotes/{quote_data['id']}" class="button">Ver Orçamento</a>
            </div>
            <div class="footer">
                <p>Este é um email automático, por favor não responda.</p>
                <p>&copy; Proteus.lab</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, recipient, html_content)

def send_advanced_quote_notification(quote_data):
    """
    Send an email notification for a new advanced quote request with detailed information
    """
    recipient = "cscheidegger@gmail.com"  # Fixed recipient as requested
    subject = f"Novo Orçamento Detalhado - #{quote_data['id']}"
    
    # Create HTML content for the email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #9b87f5; color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9fafb; }}
            .info-section {{ background-color: #f0f0ff; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
            .info-section h3 {{ margin-top: 0; color: #4f46e5; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #6b7280; }}
            .button {{ display: inline-block; background-color: #9b87f5; color: white; padding: 10px 20px; 
                      text-decoration: none; border-radius: 5px; margin-top: 15px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f8f8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Novo Orçamento Detalhado</h2>
            </div>
            <div class="content">
                <p>Olá,</p>
                <p>Um novo pedido de orçamento detalhado foi submetido com as seguintes informações:</p>
                
                <div class="info-section">
                    <h3>Informações do Cliente</h3>
                    <table>
                        <tr>
                            <td><strong>Nome:</strong></td>
                            <td>{quote_data['name']}</td>
                        </tr>
                        <tr>
                            <td><strong>E-mail:</strong></td>
                            <td>{quote_data['email']}</td>
                        </tr>
                        <tr>
                            <td><strong>Telefone:</strong></td>
                            <td>{quote_data['phone']}</td>
                        </tr>
                        <tr>
                            <td><strong>Empresa:</strong></td>
                            <td>{quote_data['company'] or 'Não informado'}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="info-section">
                    <h3>Especificações do Projeto</h3>
                    <table>
                        <tr>
                            <td><strong>Material:</strong></td>
                            <td>{quote_data['material']}</td>
                        </tr>
                        <tr>
                            <td><strong>Acabamento:</strong></td>
                            <td>{quote_data['finish']}</td>
                        </tr>
                        <tr>
                            <td><strong>Quantidade:</strong></td>
                            <td>{quote_data['quantity']}</td>
                        </tr>
                        <tr>
                            <td><strong>Prazo:</strong></td>
                            <td>{quote_data['deadline']}</td>
                        </tr>
                        <tr>
                            <td><strong>Aplicação:</strong></td>
                            <td>{quote_data['application']}</td>
                        </tr>
                        <tr>
                            <td><strong>Arquivos:</strong></td>
                            <td>{quote_data['num_files']} arquivo(s)</td>
                        </tr>
                    </table>
                </div>
                
                <div class="info-section">
                    <h3>Observações</h3>
                    <p>{quote_data['comments'] or 'Nenhuma observação adicional.'}</p>
                </div>
                
                <p><strong>ID do Orçamento:</strong> #{quote_data['id']}</p>
                <p><strong>Data:</strong> {quote_data['created_at']}</p>
                
                <p>Você pode visualizar e gerenciar este orçamento no painel administrativo:</p>
                <a href="{settings.FRONTEND_URL}/admin/quotes/{quote_data['id']}" class="button">Acessar Orçamento</a>
                
                {f'<p><strong>Acesso ao Google Drive:</strong> <a href="{quote_data["drive_url"]}">Arquivos do Projeto</a></p>' if quote_data.get('drive_url') else ''}
            </div>
            <div class="footer">
                <p>Este é um email automático, por favor não responda.</p>
                <p>&copy; Proteus.lab</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, recipient, html_content)
