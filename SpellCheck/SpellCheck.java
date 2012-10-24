import java.io.IOException;
import java.io.*;
import org.xeustechnologies.googleapi.spelling.*;
import org.xeustechnologies.googleapi.*;

public class SpellCheck {
	private static String WriteFile;
	public SpellCheck(String WriteFile)
	{
		this.WriteFile=WriteFile;
	}
	public static void main(String [] args)
	{
		/*
		 * args[0]-File path to input words for spell-check
		 * args[1]-File path you want to store the Corrected Words
		 */
		 try{
			  // Open the file that is the first 
			  // command line parameter
			 int flag=0;
			 
			 SpellCheck sc =new SpellCheck(args[1]);
			 sc. SpellingBee("");
			  FileInputStream fstream = new FileInputStream(args[0]);
			  // Get the object of DataInputStream
			  DataInputStream in = new DataInputStream(fstream);
			  BufferedReader br = new BufferedReader(new InputStreamReader(in));
			  String strLine;
			  //Read File Line By Line
			  
			  while ((strLine = br.readLine()) != null)   {
			  // Print the content on the console
			
			  String temp=strLine.toString().trim();
			  sc.SpellingBee(temp);
			  //System.out.println(strLine);
			  }
			  //Close the input stream
			  in.close();
			    }catch (Exception e){//Catch exception if any
			  System.err.println("Error: " + e.getMessage());
			  }
			  }
	   
		
	
public void SpellingBee(String st)
{
//	 Proxy settings
	 try{ 
	Configuration config = new Configuration();
	 config.setProxy( "http-proxy.corporate.ge.com", 80, "http" );
     
	 SpellChecker checker = new SpellChecker( config );
	 checker.setOverHttps( true ); // Use https (default true from v1.1)
	 checker.setLanguage( Language.ENGLISH ); // Use English (default)
     System.out.println(st);
	 SpellRequest request = new SpellRequest();
	 request.setText(st.toString().trim());
	 request.isIgnoreDuplicates(); // Ignore duplicates
     
	 SpellResponse spellResponse = checker.check( request );
     SpellCorrection [] sc=spellResponse.getCorrections();
     //for (int i=0;i<sc.length;i++)
     String []temp=sc[0].getWords();
     System.out.println(temp[0]+" "+temp[1]);
     if (temp[0].isEmpty())
    	 temp[0]="\\";
     WriteFile(st.toString().trim(),temp[0]);
     
	 }
	 catch(Exception E)
	 {
		 System.out.println("Not Found");
	 }
}
public void WriteFile(String Word,String CWord)
{
	try{
		  // Create file 
		  FileWriter fstream = new FileWriter(WriteFile,true);
		  BufferedWriter out = new BufferedWriter(fstream);
		  out.write(Word+" "+CWord+"\n");
		  //Close the output stream
		  out.close();
		  }catch (Exception e){//Catch exception if any
		  System.err.println("Error: " + e.getMessage());
		  }
		  }
}


