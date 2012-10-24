import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

import opennlp.tools.sentdetect.SentenceDetectorME;
import opennlp.tools.sentdetect.SentenceModel;

import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;

import edu.stanford.nlp.tagger.maxent.MaxentTagger;

import java.io.*;
import java.util.*;
import java.lang.System;
import java.io.IOException;
import java.io.*;
import java.util.*;

import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import opennlp.tools.sentdetect.*;

/*
 * This java Code does three things:
 * a. Reads the XML files.
 * b. Sends them to the OpenNLP sentence boundary detector to convert the text into sentences.
 * c. Sentences are POS tagged using the Stanford POS tagger.
 *
 */

public class TextReader {

	public static String TaggedFolder;

	MaxentTagger tagger;

	SentenceModel model;

	SentenceDetectorME sentenceDetector;

	public TextReader(String PacCasesFolder, String StnfrdTaggerTrainedFile,
			String OpenNLPPath, String TaggedFolder) throws IOException,
			ClassNotFoundException {
        /*
         * PacCasesFolder :args[0] wherever the PACcases in XML format are stored.
         * StnfrdTaggerTrainedFile initialises the POS tagger using the given trained file,which you should find 
         * in the Stanford POS tagger folder-args[1] ../models/bidirectional-distsim-wsj-0-18.tagger
         * OpenNLP Sentence Detector path -args[2]  ../apache-opennlp-1.5.2-incubating/bin/en-sent.bin
         * TaggedFolder:-args[3] Path to the Folder you want to store the tagged files.
         * 
         */
		tagger = new MaxentTagger(StnfrdTaggerTrainedFile);
		InitSentenceDetector(OpenNLPPath);
		sentenceDetector = new SentenceDetectorME(model);
		CreateTaggedCorpusDirectory(TaggedFolder);
		ListofFiles(PacCasesFolder);

	}

	public static void main(String[] args) throws IOException,
			ClassNotFoundException {
		TextReader text = new TextReader(args[0], args[1], args[2], args[3]);

	}

	public void InitSentenceDetector(String FilePath) throws IOException {
		/*
		 * Intialises the SentenceModel
		 */
		InputStream modelIn = new FileInputStream(FilePath);

		try {
			model = new SentenceModel(modelIn);
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (modelIn != null) {
				try {
					modelIn.close();
				} catch (IOException e) {
				}
			}
		}

	}

	public String[] SplitSentence(String Content) {
		/*
		 * Recognises the Sentence Boundaries
		 */
		String Sentences[] = sentenceDetector.sentDetect(Content);
		return Sentences;
	}

	public void Tagger(String DocumentID, String Title, String Content) {
        /*
         * Part of Speech Tagging 
         */
		String TaggedTitle;
		String TaggedSent;
		String Sentences[] = SplitSentence(Content);
		ArrayList TaggedSentences = new ArrayList();

		try {
			if (!Title.isEmpty()) {
				Title = Title.toLowerCase();
				TaggedTitle = tagger.tagString(Title);
			} else
				TaggedTitle = null;
			if (Sentences.length != 0) {
				for (int i = 0; i < Sentences.length; i++) {
					TaggedSent = tagger.tagString(Sentences[i]);
					TaggedSentences.add(TaggedSent);
					

				}
			} else
				TaggedSentences.add("");
			WriteTaggedLines(DocumentID, TaggedTitle, TaggedSentences);
		} catch (OutOfMemoryError e) {
			System.out.println("Check The Memory DocID:" + DocumentID);
		}

	}

	public void WriteTaggedLines(String DocumentID, String Title,
			ArrayList Content) {
		/*
		 * Writes the POS tagged Text in a File 
		 */
		try {

			FileWriter fstream = new FileWriter(TaggedFolder + '\\'
					+ DocumentID+".Tagged");
			BufferedWriter out = new BufferedWriter(fstream);
			fstream.write(Title);
			fstream.write("\n");
			Iterator iter = null;
			for (iter = Content.iterator(); iter.hasNext();) {
				fstream.write(iter.next().toString());
				fstream.write("\n");
			}
			fstream.close();
		} catch (Exception e) {
			e.printStackTrace();

		}
	}

	public void ReadXMLFile(File FileName) {
		/*
		 * Reads the XML files
		 */
		try {
			String DocumentPath;

			String Title;

			String Content;

			DocumentBuilderFactory dbFactory = DocumentBuilderFactory
					.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(FileName);
			doc.getDocumentElement().normalize();
			String Head = doc.getDocumentElement().getNodeName();
			NodeList nList = doc.getElementsByTagName(Head);
			for (int temp = 0; temp < nList.getLength(); temp++) {

				Node nNode = nList.item(temp);
				if (nNode.getNodeType() == Node.ELEMENT_NODE) {
					String[] ReturnList = new String[3];
					Element eElement = (Element) nNode;
					String ID = getTagValue("DocumentID", eElement);
					DocumentPath = (ID).toString();
					Title = getTagValue("Title", eElement);
					Content = getTagValue("Content", eElement);
					Tagger(DocumentPath, Title, Content);
					
				}
			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	private static String getTagValue(String sTag, Element eElement) {
		try {
			NodeList nlList = eElement.getElementsByTagName(sTag).item(0)
					.getChildNodes();
			Node nValue = (Node) nlList.item(0);
			return nValue.getNodeValue();
		} catch (Exception E) {
			return "Empty";
		}
	}

	public void CreateTaggedCorpusDirectory(String FolderPath) {
		/*
		 * Creates Folder to store the Tagged Corpus
		 */
		try {

			File file = new File(FolderPath);
			if (file.mkdir()) {
				System.out.println("Directory is created!");
				TaggedFolder = file.getCanonicalFile().toString();
			} else {
				if (!file.exists()) {
					TaggedFolder = file.getCanonicalPath().toString();
				} else {
					if (FolderPath == "") {
						System.out.println("Please Enter the Folder for the TaggedCorps");
						System.exit(0);
					} else {
						System.out.println("Folder Already Present");
						TaggedFolder=FolderPath;
					}
				}
			}

		} catch (Exception exp) {
			System.out.println("Error in Creating the Directory DefaultFolder");

		}

	}

	public void ListofFiles(String PacCasesFolder) {
/*
 * Generates the List of the Files in the Specificed Folder
 */
		try {
			File folder = new File(PacCasesFolder);
			File[] listOfFiles = folder.listFiles();

			for (int i = 0; i < listOfFiles.length; i++) {
				File XmlFile = new File(listOfFiles[i].getCanonicalPath());
				ReadXMLFile(XmlFile);
				System.out.println("FileNumber " + listOfFiles[i].getName());
			}

		} catch (Exception exe) {
			System.out.println("Folder not found");
		}

	}

}