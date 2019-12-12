#include <bits/stdc++.h>
using namespace std;

int main(){
	system("ls >> filesNew.txt");
	fstream file("filesNew.txt");
	string t;
	cout << "INSERT INTO `inovarTable` (`superSimb`, `simb`, `descr`, `url`) VALUES " << endl;
	file >> t;
	cout << "('" << t << "', '" << t << "', ' Descricao " << t << "', ' URL Video " << t << "')";
	while(file >> t){
		 cout << "," << endl << "('" << t << "', '" << t << "', ' Descricao " << t << "', ' URL Video " << t << "')";
	}
	cout << ";" << endl;
	return 0;
}
