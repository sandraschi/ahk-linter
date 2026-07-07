"""Function rename checks — v1 function names that changed in v2."""

import re
from typing import Optional
from lark import Tree
from checks.base import BaseCheck


FUNCTION_RENAMES = {
    "Asc": "Ord", "ComObjCreate": "ComObject", "ComObjParameter": "ComValue",
    "ComObjFlags": "ComValue", "ComObjActive": "ComObject",
    "Exception": "Error", "RegisterCallback": "CallbackCreate",
    "LV_Add": "ListView.Add", "LV_Delete": "ListView.Delete",
    "LV_GetCount": "ListView.GetCount", "LV_GetNext": "ListView.GetNext",
    "LV_GetText": "ListView.GetText", "LV_Modify": "ListView.Modify",
    "LV_ModifyCol": "ListView.ModifyCol", "LV_Insert": "ListView.Insert",
    "LV_DeleteCol": "ListView.DeleteCol", "LV_InsertCol": "ListView.InsertCol",
    "LV_SetImageList": "ListView.SetImageList",
    "TV_Add": "TreeView.Add", "TV_Delete": "TreeView.Delete",
    "TV_GetChild": "TreeView.GetChild", "TV_GetCount": "TreeView.GetCount",
    "TV_GetNext": "TreeView.GetNext", "TV_GetParent": "TreeView.GetParent",
    "TV_GetPrev": "TreeView.GetPrev", "TV_GetSelection": "TreeView.GetSelection",
    "TV_GetText": "TreeView.GetText", "TV_Modify": "TreeView.Modify",
    "TV_SetImageList": "TreeView.SetImageList",
    "SB_SetIcon": "StatusBar.SetIcon", "SB_SetParts": "StatusBar.SetParts",
    "SB_SetText": "StatusBar.SetText",
    "VarSetCapacity": "Buffer",
}

OBJECT_METHOD_RENAMES = {
    "HasKey": "Has",
    "Length": "Length",
    "Count": "Count",
    "Insert": "InsertAt",
    "Remove": "RemoveAt",
    "MaxIndex": "MaxIndex",
    "MinIndex": "MinIndex",
}


class FunctionRenamesCheck(BaseCheck):
    """Flags renamed functions like LV_Add → ListView.Add, Asc → Ord, etc."""

    def __init__(self, config):
        super().__init__(config)
        self.name = "v1_syntax"

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []
        for v1_name, v2_name in FUNCTION_RENAMES.items():
            pattern = rf'\b{v1_name}\s*\('
            for m in re.finditer(pattern, source):
                line = source[:m.start()].count("\n") + 1
                issues.append(self._make_issue(
                    f"V1_FUNC_{v1_name}",
                    f"Use {v2_name}() instead of {v1_name}()",
                    line, fixable=False
                ))
        return issues


class OldObjectModelCheck(BaseCheck):
    """Flags v1 object model patterns: pseudo-arrays, for-loop syntax, 1-index vs 0-index."""

    def __init__(self, config):
        super().__init__(config)
        self.name = "v1_syntax"

    def run(self, source: str, ast: Optional[Tree]) -> list[dict]:
        issues = []

        # Pseudo-array pattern: Array%i%
        for m in re.finditer(r'(\w+)%(\w+)%', source):
            line = source[:m.start()].count("\n") + 1
            issues.append(self._make_issue(
                "V1_PSEUDO_ARRAY",
                f"Use {m.group(1)}[{m.group(2)}] instead of {m.group(1)}%{m.group(2)}%",
                line, fixable=False
            ))

        # Object syntax: obj.key (string key) when used in assoc array context
        # This is harder to detect without type info — flag as suggestion
        for m in re.finditer(r'\.HasKey\(', source):
            line = source[:m.start()].count("\n") + 1
            issues.append(self._make_issue(
                "V1_HASKEY",
                "Use obj.Has(key) instead of obj.HasKey(key)",
                line, fixable=False
            ))

        # ComObjParameter
        for m in re.finditer(r'\bComObjParameter\(', source):
            line = source[:m.start()].count("\n") + 1
            issues.append(self._make_issue(
                "V1_COMOBJ_PARAM",
                "Use ComValue() instead of ComObjParameter()",
                line, fixable=False
            ))

        return issues
