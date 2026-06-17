import type { ChatCitation } from "@/lib/api/types";
import type { SourceCard } from "@/types/studio";

export function citationsToSourceCards(citations: ChatCitation[]): SourceCard[] {
  return citations.map((citation, index) => {
    const location = citation.floor
      ? `${citation.floor} 楼`
      : citation.page_start
        ? `p.${citation.page_start}`
        : citation.page ?? "source";

    const tags = [citation.document_kind, citation.author, citation.topic].filter((tag): tag is string =>
      Boolean(tag),
    );

    return {
      id: citation.item_id ?? `${citation.source}-${index + 1}`,
      rank: index + 1,
      title: citation.source,
      page: location,
      score: "1.00",
      quote: citation.quote ?? citation.item_id ?? "结构化引用",
      tags,
    };
  });
}
