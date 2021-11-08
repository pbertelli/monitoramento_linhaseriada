<html>
 <head>
  <title>Tela de Monitoramento</title>
  <meta charset="utf-8">

 </head>
 <body>
 	<div class="title" align="center">
 		<style type="text/css">
			
			body{
				background-color: #000000;
				color: #FFFFFF;
				margin-left: 15%;
				margin-right: 15%;
			}
			h1 { font-family: Corbel, monaco, monospace; font-size: 22px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 26.4px; }
			h2 { font-family: Corbel, monaco, monospace; font-size: 19px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 15.4px; } 
			h3 { font-family: Corbel, monaco, monospace; font-size: 16px; font-style: normal; font-variant: normal; font-weight: normal; line-height: 15.4px; }

			/* criação de blocos*/

				.square{
				    width: 14.6%;
				    height: 0; /* A mágica está aqui */
				    padding-bottom: 15%; /* ... e está aqui */
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

		function horasdecimais($time) {

			$hms = explode(":", $time);
			return ($hms[0] + ($hms[1]/60) + ($hms[2]/3600));

		}

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
		$result_flag = mysqli_query($con,"SELECT * FROM flag");
		$result_tempo = mysqli_query($con,"SELECT * FROM tempo");
		$result_tempo2 = mysqli_query($con,"SELECT * FROM tempo");
		$result_tempo3 = mysqli_query($con,"SELECT * FROM tempo");

		$linhas=mysqli_num_rows($result);

		$nconf = 0;


		
		//pegando a flag de erro
		$row1 = mysqli_fetch_array($result_flag);
		if($row1['flag'] == 2) {
				echo "<script>alert('O Sistema Parou');</script>";
		}



		$row1 = mysqli_fetch_array($result_flag);

		$linhas=mysqli_num_rows($result);
		$linhas_tempo=mysqli_num_rows($result_tempo);

		$nconf = 0;
		$tempo_ligado = 0;
		$tempo_desligado = 0;
		$tempo_parado = 0;
		$tempo_inteiro = 0;
		$tempo_inicio = 0;


		//CALCULO DO TEMPO LIGADO
		for($i=0; $i<$linhas_tempo; $i++)
		{

				$row_tempo = mysqli_fetch_array($result_tempo);
				//média de tempos

				if($row_tempo['tempo_ligado'])
					$tempo_zero = $row_tempo['tempo_ligado'];
				if($row_tempo['tempo_desligado']){
					$tempo_completo = $row_tempo['tempo_desligado'];
				}
				elseif ($row_tempo['tempo_parado']) {
					$tempo_completo = $row_tempo['tempo_parado'];
				}

				if ((strtotime($tempo_completo) - strtotime("00:00:00")) > 0)
					$tempo_ligado = $tempo_ligado + (strtotime($tempo_completo) - strtotime($tempo_zero));
		}
		
		//CALCULO DO TEMPO DESLIGADO
		for($i=0; $i<$linhas_tempo; $i++)
		{
				$row_tempo = mysqli_fetch_array($result_tempo2);
				//média de tempos

				if((strtotime($row_tempo['tempo_desligado']) - strtotime("00:00:00")) > 0){
					$tempo_inicio = $row_tempo['tempo_desligado'];
				}
				if((strtotime($row_tempo['tempo_ligado']) - strtotime("00:00:00")) > 0){
					$tempo_inteiro = $row_tempo['tempo_ligado'];
				}

				if ((strtotime($tempo_inteiro) - strtotime("00:00:00")) > 0)
					$tempo_desligado = $tempo_desligado + (strtotime($tempo_inteiro) - strtotime($tempo_inicio));
		}

		//CALCULO DO TEMPO PARADO
		for($i=0; $i<$linhas_tempo; $i++)
		{
				$row_tempo = mysqli_fetch_array($result_tempo3);
				//média de tempos

				if((strtotime($row_tempo['tempo_parado']) - strtotime("00:00:00")) > 0){
					$tempo_inicio = $row_tempo['tempo_parado'];
				}
				if((strtotime($row_tempo['tempo_ligado']) - strtotime("00:00:00")) > 0){
					$tempo_inteiro = $row_tempo['tempo_ligado'];
				}

				if ((strtotime($tempo_inteiro) - strtotime("00:00:00")) > 0)
					$tempo_parado = $tempo_parado + (strtotime($tempo_inteiro) - strtotime($tempo_inicio));
		}

		$tempo_operacao = $tempo_ligado+$tempo_desligado+$tempo_parado;



		$operacao_dec = horasdecimais(gmdate("H:i:s", $tempo_operacao));
		$desligado_dec = horasdecimais(gmdate("H:i:s", $tempo_desligado));
		$parado_dec = horasdecimais(gmdate("H:i:s", $tempo_parado));

		$tempo_produzindo = $operacao_dec - $desligado_dec;


		$disponibilidade = 100*$tempo_produzindo/$operacao_dec;

		$performance = 100*($tempo_produzindo - $parado_dec)/$tempo_produzindo;



		
		for($i=0; $i<$linhas; $i++)
		{
				//contagem de conformes
				$row = mysqli_fetch_array($result);
				if($row['qtd_ok']){
					$nconf++;
				}

				//média de tempos
				if($i == 0)
					$tempo_inicial = $row['horario'];
				if($i == $linhas-1)
					$tempo_final = $row['horario'];
				
		}
			

		//contagem de inconformes
		$ninconf = $linhas - $nconf;


		//qualidade obtida
		$quality = ($nconf/$linhas)*100;

		//tempo ligado
		$time_total = (strtotime($tempo_final) - strtotime($tempo_inicial));

		//calculo de OEE
		$oee = ($quality * $performance * $disponibilidade)/10000;







		?>


		



		<h3>UTFPR - Universidade Tecnologica Federal do Paraná - Campus Campo Mourão</h3>
		<h1><b>PROJETO DE UM SISTEMA EMBARCADO PARA MONITORAMENTO DE UMA ESTEIRA INDUSTRIAL UTILIZANDO VISÃO COMPUTACIONAL</b></h1>

		<h3>Acadêmico: Pedro Bertelli</h3>
		<h3>Orientador: Prof. Ms. Lucas Ricken Garcia</h3>

		
		<br/>
		<?php
				echo "SISTEMA <font size: 60 color='#FFFF00'>PARADO</font>";	
		?>
		<br>
		<br>
		<form action="monitoramento.php" method="post">
			<input type="hidden" value="1" name=na>
			<input type=submit value="Reiniciar">
			
		</form>

		<br/>
		<br/>

		 
		 <div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>Total de Produtos:</h3>
		            <h1>
		            	<?php
		            	
		            	echo $linhas;

		            	?>
		            </h1>
		        </div>
		        
		    </div>
		</div>

		<div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>Produtos Conformes:</h3>
		            <h1>
		            	<?php
		            	
		            	echo $nconf;

		            	?>
		            </h1>
		        </div>
		        
		    </div>
		</div>

		<div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>Produtos Inconformes:</h3>
		            <h1>
		            	<?php
		            	
		            	echo $ninconf;

		            	?>
		            </h1>
		        </div>
		        
		    </div>
		</div>

		<div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>Qualidade obtida:</h3>
		            <h1>
			            <?php
			            	
			            	if($quality >= 0)
				            	echo number_format($quality,2).'%';
				            else
				            	echo '0%';

			            ?>
		            </h1>
		        </div>
		        
		    </div>
		</div>

		<div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>OEE:</h3>
		            <h1>
		            	<?php
			            	
			            	if($oee >= 0)
				            	echo number_format($oee,2).'%';
				            else
				            	echo '0%';

			            ?>
		            </h1>
		        </div>
		        
		    </div>
		</div>

		<div class="square">
		    <div class="block">
		        
		        <div class="centered">
		            <h3>Tempo de Funcionamento:</h3>
		            <h1>
			            <?php
			            	
			            	echo gmdate("H:i:s", $time_total);
			            	#echo number_format($time_total).' s';

			            ?>
		            </h1>
		        </div>
		        
		    </div>
		</div>


		
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<br/>
		<h2><a href="monitoramento.php">MONITORAMENTO</a> | <a href="relatorio.php">TELA DE RELATÓRIO</a></h2>


	</div>
 </body>
</html>