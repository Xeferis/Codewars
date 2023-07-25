class document:
    def __init__(self, info: dict):
        self.__keys = info.keys()
        if "ID#" in self.__keys:
            self.id = info["ID#"]
        self._lname = info["NAME"].split(',')[0].strip()
        self._fname = info["NAME"].split(',')[1].strip()
        if "NATION" in self.__keys:
            self.nation = info["NATION"]
        if "EXP" in self.__keys:
            self._expiration = list(map(int, info["EXP"].split(".")))

    def __str__(self):
        return str(self.__class__.__name__)

    def __repr__(self):
        return str(self.__class__.__name__)

    @property
    def name(self) -> str:
        return self._fname + " " + self._lname

    @property
    def exp(self) -> list:
        if "EXP" in self.__keys:
            return self._expiration

    @exp.setter
    def exp(self, date: str):
        if "EXP" in self.__keys:
            self._expiration = list(map(int, date.split(".")))

    def valid(self, current_date: list) -> bool:
        if "EXP" in self.__keys:
            if current_date[0] > self.exp[0]:
                return False
            else:
                if current_date[0] == self.exp[0] and current_date[1] > self.exp[1]:
                    return False
                else:
                    if current_date[0] == self.exp[0] and current_date[1] == self.exp[1] and current_date[2] > self.exp[2]:
                        return False
        return True


class passport(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self._dob = list(map(int, info["DOB"].split(".")))
        self.sex = info["SEX"]
        self.iss = info["ISS"]

    @property
    def dob(self) -> list:
        return self._dob

    @dob.setter
    def dob(self, date: str):
        self._dob = list(map(int, date.split(".")))


class work_pass(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self.height = info["FIELD"]


class certificate_of_vaccination(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self.vaccs = info["VACCINES"]


class ID_card(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self._dob = list(map(int, info["DOB"].split(".")))
        self.height = info["HEIGHT"]
        self.weight = info["WEIGHT"]

    @property
    def dob(self) -> list:
        return self._dob

    @dob.setter
    def dob(self, date: str):
        self._dob = list(map(int, date.split(".")))


class diplomatic_authorization(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self.access = info["ACCESS"]

    def valid(self, current_date: list) -> bool:
        if "Arstotzka" in self.access:
            return True
        return False


class grant_of_asylum(document):
    def __init__(self, info: dict):
        super().__init__(info)
        self.height = info["HEIGHT"]
        self.weight = info["WEIGHT"]


class access_permit(grant_of_asylum):
    def __init__(self, info: dict):
        super().__init__(info)
        self.purpose = info["PURPOSE"]
        self._duration = info["DURATION"].split()[0]

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, dur: str):
        if dur == "FOREVER":
            self._duration = 10000*10000
        else:
            self._duration = int(dur.split()[0])


class person:
    def __init__(self, info: dict):
        self.__country = "Arstotzka"
        self.docs = []
        self.passed = False

        for doc in info:
            tmp_info = {}
            for r in info[doc].split("\n"):
                k_v = r.split(":")
                tmp_info[k_v[0].strip()] = k_v[1].strip()
            if doc == "passport":
                pp = passport(tmp_info)
                self.docs.append(pp)
            elif doc == "diplomatic_authorization":
                da = diplomatic_authorization(tmp_info)
                self.docs.append(da)
            elif doc == "access_permit":
                ap = access_permit(tmp_info)
                self.docs.append(ap)
            elif doc == "grant_of_asylum":
                ga = grant_of_asylum(tmp_info)
                self.docs.append(ga)
            elif doc == "ID_card":
                idc = ID_card(tmp_info)
                self.docs.append(idc)
            elif doc == "work_pass":
                wp = work_pass(tmp_info)
                self.docs.append(wp)
            elif doc == "certificate_of_vaccination":
                cov = certificate_of_vaccination(tmp_info)
                self.docs.append(cov)
            else:
                print(f"{doc}: Unknown Document!")
                print(tmp_info)

    def documents_valid(self, date) -> dict:
        tmp = {}
        for doc in self.docs:
            if doc.valid(date):
                tmp[str(doc)] = True
            else:
                tmp[str(doc)] = False
        return tmp

    def documents_correct(self) -> bool:
        tmp = []
        tmp_keys = []
        for doc in self.docs:
            tmp_keys.append(doc.__dict__.keys())
            tmp.append(doc.__dict__)
        if len(tmp) > 1:
            for key in tmp[0]:
                for dict in tmp[1::]:
                    if key in dict.keys():
                        # Key not there
                        if tmp[0][key] != dict[key] and key != "_expiration" and key != "_document__keys":
                            return False, key

                        if key == "_dob":
                            for i, val in enumerate(tmp[0][key]):
                                if val != dict[key][i]:
                                    return False, "Birthday"
                        elif key != "_expiration" and key != "_document__keys":
                            if tmp[0][key] != dict[key]:
                                return False, key
        return True, None

    def is_banned(self, denied: list, allowed) -> bool:
        if self.country in denied or self.country not in allowed:
            return True
        return False

    def is_vacced(self, vaccs: dict) -> bool:
        needed_personal = []
        for vacc in vaccs:
            if self.origin in vaccs[vacc] or self.country in vaccs[vacc] or "Entrants" in vaccs[vacc]:
                needed_personal.append(vacc)
        if self.vaccs is None and len(needed_personal) == 0:
            return True
        elif self.vaccs is None and len(needed_personal) > 0:
            return False
        else:
            for n_vac in needed_personal:
                if n_vac.split()[0] not in self.vaccs:
                    return False
        return True

    @property
    def vaccs(self):
        for doc in self.docs:
            if str(doc) == "certificate_of_vaccination":
                return doc.vaccs
        return None

    @property
    def origin(self):
        tmp = "Foreigner"
        for doc in self.docs:
            if str(doc) != "ID_card" and str(doc) != "certificate_of_vaccination" and str(doc) != "work_pass":
                try:
                    if doc.purpose == "WORK":
                        tmp = "Worker"
                    else:
                        if doc.nation == self.__country:
                            tmp = "Citizen"
                        else:
                            tmp = "Foreigner"
                except:
                    if doc.nation == self.__country:
                        tmp = "Citizen"
                    else:
                        tmp = "Foreigner"
        return tmp

    @property
    def name(self):
        var = None
        for doc in self.docs:
            tmp = doc.name
            if doc.name == tmp:
                var = doc.name
            else:
                return "Invalid Name. No the same in all Docs"
        return var

    @property
    def country(self):
        var = None
        for doc in self.docs:
            if str(doc) != "ID_card" and str(doc) != "certificate_of_vaccination" and str(doc) != "work_pass":
                tmp = doc.nation
                if doc.nation == tmp:
                    var = doc.nation
                else:
                    return "Invalid country. No the same in all Docs"
        return var


class Inspector:
    def __init__(self):
        self.curr_date = [1982, 11, 22]
        self.allowed = []
        self.denied = []
        self.wanted = []
        self.doc_req = {
            'Foreigners': [],
            'Citizens': [],
            'Workers': []
        }
        self.vacc_req = {}

    def receive_bulletin(self, bulletin: str):
        for row in bulletin.split("\n"):

            if "Allow citizens" in row:
                info = row.split("of")[-1]

                if len(info) > 1:
                    infos = info.split(",")

                    for info in infos:
                        self.allowed.append(info.strip())

                        if info.strip() in self.denied:
                            self.denied.remove(info.strip())
                else:
                    self.allowed.append(info.strip())
                    if info.strip() in self.denied:

                        self.denied.remove(info.strip())

            elif "Deny citizens" in row:
                info = row.split("of")[-1]

                if len(info) > 1:
                    infos = info.split(",")
                    for info in infos:
                        self.denied.append(info.strip())

                        if info.strip() in self.allowed:
                            self.allowed.remove(info.strip())
                else:
                    self.denied.append(info.strip())

                    if info in self.allowed:
                        self.allowed.remove(info.strip())
            elif "require" in row and "vaccination" not in row:
                info = row.split("require")
                p_class = info[0].strip()
                p_doc = info[1].strip().replace(" ", "_")

                if p_class == "Citizens of Arstotzka":
                    self.doc_req["Citizens"].append(p_doc)
                elif p_class == "Entrants":
                    for k in self.doc_req:
                        self.doc_req[k].append(p_doc)
                else:
                    self.doc_req[p_class].append(p_doc)
            elif "require" in row and "vaccination" in row and "no longer" not in row:
                info = row.split("require")
                vacc = info[-1].strip()
                country = list(
                    map(str.strip, info[0].split("of")[-1].split(",")))
                self.vacc_req[vacc] = country
            elif "no longer require" in row and "vaccination" in row:
                info = row.split("no longer require")
                person = info[0].strip()
                vacc = info[-1].strip()
                if person == "Entrants":
                    self.vacc_req.pop(vacc)
                else:
                    country = list(
                        map(str.strip, person.split("of")[-1].split(",")))
                    for c in country:
                        if c in self.vacc_req[vacc]:
                            self.vacc_req[vacc].remove(c)
            elif "Wanted" in row:
                wanted_p = row.split(":")[-1].strip()
                self.wanted.append(wanted_p)

    def inspect(self, personalinfo):
        infos_outs = {
            "id": "ID number",
            "nation": "nationality",
            "_dob": "date of birth",
            "_lname": "name",
            "_fname": "name"
        }
        if personalinfo:
            p = person(personalinfo)
            v_docs = p.documents_valid(self.curr_date)
            docs = list(map(str, p.docs))
            docs_bl, doc_val = p.documents_correct()
            p_ori = p.origin
            vacced = p.is_vacced(self.vacc_req)

            if p_ori == "Foreigner" and len(v_docs) == 0:
                return 'Entry denied: missing required passport.'

            if p.name in self.wanted:
                return "Detainment: Entrant is a wanted criminal."

            if not docs_bl:
                return f"Detainment: {infos_outs[doc_val]} mismatch."

            for d in self.doc_req[p_ori+"s"]:
                if d not in docs:
                    if p_ori == "Citizen" and "grant_of_asylum" in docs and d == "ID_card":
                        pass
                    elif p_ori == "Foreigner" and "passport" in docs and "diplomatic_authorization" in docs:
                        pass
                    elif p_ori == "Foreigner" and "passport" in docs and "grant_of_asylum" in docs:
                        pass
                    else:
                        return f'Entry denied: missing required {d.replace("_", " ")}.'

            if p.name in self.wanted:
                return "Detainment: Entrant is a wanted criminal."

            if p.is_banned(self.denied, self.allowed):
                return 'Entry denied: citizen of banned nation.'

            for d in v_docs:
                if not v_docs[d]:
                    filler = d.replace('_', ' ')
                    if 'diplomatic' in filler:
                        return f"Entry denied: invalid diplomatic authorization."
                    return f"Entry denied: {filler} expired."

            if not vacced:
                return 'Entry denied: missing required vaccination.'

            if p_ori == "Citizen":
                return "Glory to Arstotzka."
            else:
                return "Cause no trouble."
        return 'Entry denied: missing required passport.'
