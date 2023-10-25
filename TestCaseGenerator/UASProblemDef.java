package org.uma.jmetal.problem.singleobjective;

import org.uma.jmetal.problem.doubleproblem.impl.AbstractDoubleProblem;
import org.uma.jmetal.solution.doublesolution.DoubleSolution;


import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Scanner;
import java.util.concurrent.CompletableFuture;

/**
 * Class representing a Sphere problem.
 */
@SuppressWarnings("serial")
public class SphereUAS2 extends AbstractDoubleProblem {
  /** Constructor */
  public SphereUAS2() {
    this(21) ;
   //gatewayServer2 = new GatewayServer(new SphereUAS(),25336);
    
  }
  
  /** Constructor */
  public SphereUAS2(Integer numberOfVariables) {
    setNumberOfVariables(numberOfVariables);
    setNumberOfObjectives(1);
    setName("SphereUAS2");
    
    List<Double> lowerLimit = new ArrayList<>(getNumberOfVariables()) ;
    List<Double> upperLimit = new ArrayList<>(getNumberOfVariables()) ;
    

  //vibrationLevel
    lowerLimit.add(0.0);
    upperLimit.add(40.0);
    
    
    //GPS Connection
    lowerLimit.add(0.0); 
    upperLimit.add(1.0);

    //RC Connection
    lowerLimit.add(0.0);
    upperLimit.add(1.0);
    
    //Wind Speed
    lowerLimit.add(20.0);
    upperLimit.add(40.0);
    
   
//    //lat1
    lowerLimit.add(-90.0);
    upperLimit.add(90.0);
//    //long1
    lowerLimit.add(-180.0);
    upperLimit.add(180.0);
//    
//    //lat2
    lowerLimit.add(-90.0);
    upperLimit.add(90.0);
//    //long2
    lowerLimit.add(-180.0);
    upperLimit.add(180.0);
//    
//    //lat3
    lowerLimit.add(-90.0);
    upperLimit.add(90.0);
//    //long3
    lowerLimit.add(-180.0);
    upperLimit.add(180.0);
//    
//    //lat4
    lowerLimit.add(-90.0);
    upperLimit.add(90.0);
//    //long4
    lowerLimit.add(-180.0);
    upperLimit.add(180.0);
    
	//  //lat5
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long5
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);
	//  
	//  //lat6
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long6
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);
	//  
	//  //lat7
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long7
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);
	//  
	//  //lat8
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long8
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);
	  
	//lat9
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long9
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);
	//  
	//  //lat10
	  lowerLimit.add(-90.0);
	  upperLimit.add(90.0);
	//  //long10
	  lowerLimit.add(-180.0);
	  upperLimit.add(180.0);

    
    setVariableBounds(lowerLimit, upperLimit);


  }
  
 
  public int solutionIndex = -1;
  public void setSolutionIndex(int s)
  {
	  this.solutionIndex=s;
  }
  public int getSolutionIndex()
  {
	  return this.solutionIndex;
  }
  
  public String solutionpath="";
  public void writeSolToFile(DoubleSolution solution, int solutionID)
  {
	  
	  	int restorePop = 0;
	    String restorefilename = "restorefilename";
	    //getting restart UAS value 
	    try {
	        File myObj = new File(restorefilename);
	        Scanner myReader = new Scanner(myObj);
	        while (myReader.hasNextLine()) {
	          String data = myReader.nextLine();
	          if(data.contains("populationCounter:"))
	          {
	        	  String arr[] = data.split(":");
	        	  restorePop = Integer.valueOf(arr[1]);
	          }
	        //  System.out.println(data);
	        }
	        myReader.close();
	      } catch (FileNotFoundException e) {
	        System.out.println("No restore file created yet");
	        e.printStackTrace();
	      }
	    
	//writing  solution to file
	  
	    try {
	    	
	    			String filepathToStoreSolution = "D:\\GApopulation\\populationRes.txt";
			    		
	    				solutionpath = filepathToStoreSolution;
			    		File file = new File(solutionpath);
			    		if (!file.exists())
			    		{
				            FileWriter fr = new FileWriter(file, true);
				            BufferedWriter br = new BufferedWriter(fr);
				            PrintWriter pr = new PrintWriter(br); 
				            for (int i = 0; i<solution.getNumberOfVariables(); i++) {
				            	pr.print(solution.getVariable(i)+",");
				            } 
				            pr.close();
				           	br.close();
				           	fr.close();
			    		}
			        
			    //	} 
	   	 
	        	} catch (IOException e) {
	    		// TODO Auto-generated catch block
	        			e.printStackTrace();
	    	}
  }
  public void writeDistanceToFile(double distance)
  {
	//writing distance to file
	    try {
	    	
	    		String filepathToStoreSolution = "D:\\GApopulation\\populationRes.txt";
	    		File file = new File(filepathToStoreSolution);
	            FileWriter fr = new FileWriter(file, true);
	            BufferedWriter br = new BufferedWriter(fr);
	            PrintWriter pr = new PrintWriter(br);
//	            for (int i = 0; i<solution.getNumberOfVariables(); i++) {
//	            	//pr.print(solution.getVariable(i)+",");
//	            } 
	            pr.print(distance); //saving objectives values in file
	            pr.print("\n");
	            pr.close();
	           	br.close();
	           	fr.close();
	        
	    	 
	   	 
	        	} catch (IOException e) {
	    		// TODO Auto-generated catch block
	    		e.printStackTrace();
	    	}
  }
  
  /** Evaluate() method */
  @Override

  /** Evaluate() method */
//  @Override
  public void evaluate(DoubleSolution solution) {
    int numberOfVariables = getNumberOfVariables() ;

    Double distance = 0.0;
    double[] x = new double[numberOfVariables] ;
    String message = "";
    
    String solutionpath="";
    
    
  
	    Boolean restartUAS = null;
	    String restorerestartfilename = "nameofrestorerestartfile";
	    //getting restart UAS value 
	    try {
	        File myObj = new File(restorerestartfilename);
	        Scanner myReader = new Scanner(myObj);
	        while (myReader.hasNextLine()) {
	          String data = myReader.nextLine();
	          if(data.contains("restartUAS:"))
	          {
	        	  String arr[] = data.split(":");
	        	  restartUAS = Boolean.valueOf(arr[1]);
	          }
	        //  System.out.println(data);
	        }
	        myReader.close();
	      } catch (FileNotFoundException e) {
	        System.out.println("No restore file created yet");
	        e.printStackTrace();
	      }
	   
    
    if (restartUAS==true && solution.getObjective(0)!=0.0) //if objective value is not 0.0 then it is not required to be evaluated
    {
    	distance = solution.getObjective(0);
    }
    else
    {
    		//========Sending solution for evaluation
		    try {
		    	ServerSocket Server = new ServerSocket (2004);
		    	Server.setReuseAddress(true);
		    	System.out.println ("TCPServer Waiting for client on port 2004");
		        Socket connected = Server.accept();
		        System.out.println( " THE CLIENT"+" "+ connected.getInetAddress() +":"+connected.getPort()+" IS CONNECTED ");
		
		        DataOutputStream dout=new DataOutputStream(connected.getOutputStream()); 
		        dout.writeUTF(solution.getVariables().toString());
		        
		        
		       
		          dout.close();connected.close();Server.close();       
		        
		        }
		    	catch(Exception e){
		            e.printStackTrace();}
		    //===========End sending solution
		    
		    //==========Receiving fitness value for solution
		    	try {
		        	ServerSocket Server1 = new ServerSocket (5000);
		        	Server1.setReuseAddress(true);
		        	System.out.println ("TCPServer Waiting for data from client on port 5000");
		            Socket connected1 = Server1.accept();
		            System.out.println( " THE CLIENT"+" "+ connected1.getInetAddress() +":"+connected1.getPort()+" IS CONNECTED ");
		
		             BufferedReader in = new BufferedReader(new InputStreamReader(connected1.getInputStream()));
		            message = in.readLine();
		            
		            System.out.println("Message Received: "+message);
		            in.close();
		           
		            connected1.close();
		            Server1.close();       
		            
		            }
		        	catch(Exception e){
		                e.printStackTrace();
		                }
		    //========End Receiving evaluation result from python client
		    	
    	
    	
	
		    message = message.substring(1, message.length() - 1);
		    distance=Double.parseDouble(message);
    writeDistanceToFile(distance);
    
    }
    
    //end writing distance to file
    System.out.print("Distance,AVG: "+distance);
    solution.setObjective(0, distance);
    
    
    
  } 
  
  
}

