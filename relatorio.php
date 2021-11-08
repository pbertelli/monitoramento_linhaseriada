<html>
 <head>
  <title>Tela de Relatório</title>
 </head>
 <body>
 	<div class="title" align="center">
 		<style type="text/css">

 			form {
			    /* Apenas para centralizar o form na página */
			    margin: 0 auto;
			    width: 400px;
			}



			body{
				background-color: #000000;
				color: #FFFFFF;
				margin-left: 15%;
				margin-right: 15%;
				text-align: center;
			}
			h1 { font-family: Corbel, monaco, monospace; font-size: 22px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 26.4px; }
			h2 { font-family: Arial, monaco, monospace; font-size: 19px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 15.4px; } 
			h3 { font-family: Corbel, monaco, monospace; font-size: 16px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 15.4px; }

			td {
			  text-align: center;
			  vertical-align: middle;
			}

			/* criação de blocos*/

				.square{
				    width: 14.6%;
				    height: 0;
				    padding-bottom: 15%;
				    margin: 1%;
				    float: left;
				    position: relative;
				}
				.block{
				  position: absolute;
				  text-align: center;
				  background: #1a1a1a;
				  width: 100%;
				  height: 100%;
				}
				 
				.block:before {
				  content: '';
				  display: inline-block;
				  height: 100%;
				  vertical-align: middle;
				  margin-right: -0.25em;
				 }
				 
				.centered {
				  display: inline-block;
				  vertical-align: middle;
				  width: 80%;
				  background: #222;
				  color: #FFF;
				 }		

			/* finaliza criação de blocos*/	 	

		</style>

		<!-- Conectando com o banco de dados MySQL
		-->

		<?php

		$hostname = "localhost";
		$username = "root";
		$password = "";
		$dbname = "relatorio";
		$usertable = "valores";

		$con = mysqli_connect($hostname, $username, $password, $dbname);

		if (mysqli_connect_errno())
		{
		echo "Failed to connect to MySQL: " . mysqli_connect_error();
		}

		$result = mysqli_query($con,"SELECT * FROM $usertable");

		$linhas=mysqli_num_rows($result);


		?>


		



		<h3>UTFPR - Universidade Tecnologica Federal do Paraná - Campus Campo Mourão</h3>
		<h1><b>PROJETO DE UM SISTEMA EMBARCADO PARA MONITORAMENTO DE UMA ESTEIRA INDUSTRIAL UTILIZANDO VISÃO COMPUTACIONAL</b></h1>

		<h3>Acadêmico: Pedro Bertelli</h3>
		<h3>Orientador: Prof. Ms. Lucas Ricken Garcia</h3>

		
		<br/>
		<h2>ESCOLHA UM DIA PARA GERAR O RELATÓRIO</font></h2>
		<br/>
		<br/>



		<form action="relatorio_action.php" method="post">
			Data: <input type=date name=data>
			<input type=submit value="OK">
			<br>
			<br>
		</form>
		

		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<h2><a href="/monitoramento.php">MONITORAMENTO</a> | <a href="/relatorio.php">TELA DE RELATÓRIO</a></h2>


	</div>
 </body>
</html>